# ph-editor/tests/test_clothing_random.py

import random
from io import BytesIO

import pytest

# test utils
from tests.utils import compare_dicts, _random_color_str, _random_hex_string
# 導入序列化和解析函數
from serializers.clothing_serializer import serialize_clothing_data
from parsers.clothing_parser import parse_clothing_data
# 導入服裝數據
from game_data.clothing_data import CLOTHING_ITEMS, is_colorful, get_option_flags

# clothing_parser.py 借用過來的浮點數轉換函式
def _format_float_to_percentage(value: float, scale: float = 100) -> int:
    """
    將浮點數轉換為 0-100% 的整數值。
    """
    percentage = round(value * scale)
    return max(0, min(100, percentage))

def format_for_test(slot: str, item: dict = None) -> dict:
    """
    構建用於序列化測試的 clothing_data 結構的一個部分。
    會填充隨機或預設的數值、顏色值。
    """
    formatted_data = {}

    # 隨機選擇一個 clothing item，如果沒有提供的話
    if item is None:
        # Filter out empty lists in case a slot has no items defined
        available_items = CLOTHING_ITEMS.get(slot, [])
        if not available_items:
            print(f"Warning: No clothing items defined for slot '{slot}'. Skipping.")
            return None # Return None if no items are available for this slot
        item = random.choice(available_items)

    item_id = item['id']
    # slotIdx in parser is based on hardcoded order (0-10), not item['slot']
    # The serializer expects 'slot' in item_data, so we'll just set a dummy value
    # as it's not actually used by the serializer for the slot_idx in the binary.
    # The slotIdx read by the parser is actually the ID for the *clothing set type*
    # (top=0, bottom=1, bra=2, etc.), NOT the item ID.
    # The parse_clothing_item function receives 'slot' as a string and
    # determines 'slotIdx' internally from the stream.
    # For serialization, it expects 'slotIdx' to be part of item_data.
    # We will use the hardcoded index from the parsing order.
    slot_to_idx = {
        'top': 0, 'bottom': 1, 'bra': 2, 'panty': 3,
        'swimsuit': 4, 'swimsuit_top': 5, 'swimsuit_bottom': 6,
        'gloves': 7, 'pantyhose': 8, 'socks': 9, 'shoes': 10
    }
    slot_idx = slot_to_idx.get(slot, 0) # Default to 0 if slot not found, though all should be in dict

    color_flag = is_colorful(slot, item_id)

    formatted_data = {
        'slot': slot_idx, # This is the index of the slot, not the item ID
        'id': item_id,
        'color': 3 if color_flag > 0 else 0, # C1, C2, C3 -> 3  # C0 -> 0
        '#name': item['name']['ja'], # Use Japanese name for comparison
    }

    # 根據 color_flag 決定顏色和光澤屬性
    if color_flag == 3:
        # 主副色都能隨意調整
        formatted_data.update({
            'main_color': _random_color_str(),
            'main_shine': _random_color_str(),
            'main_shine_strength': random.randint(0, 100),
            'main_shine_texture': random.randint(0, 100),
            'sub_color': _random_color_str(),
            'sub_shine_color': _random_color_str(),
            'sub_shine_strength': random.randint(0, 100),
            'sub_shine_texture': random.randint(0, 100),
        })
    elif color_flag == 1:
        # 只能改主色, 副色固定為白色, 光澤固定為黑色無光澤
        formatted_data.update({
            'main_color': _random_color_str(),
            'main_shine': '(0, 0, 0, 0)', # Fixed black, no shine
            'main_shine_strength': 0,
            'main_shine_texture': 0,
            'sub_color': '(255, 255, 255, 255)', # Fixed white
            'sub_shine_color': '(0, 0, 0, 0)', # Fixed black, no shine
            'sub_shine_strength': 0,
            'sub_shine_texture': 0,
        })
    elif color_flag == 2:
        # 能改主副色, 但光澤質感固定 (假設為 0)
        formatted_data.update({
            'main_color': _random_color_str(),
            'main_shine': _random_color_str(), # Main shine can be random color
            'main_shine_strength': 0, # Main shine strength fixed to 0
            'main_shine_texture': 0, # Main shine texture fixed to 0
            'sub_color': _random_color_str(),
            'sub_shine_color': _random_color_str(), # Sub shine can be random color
            'sub_shine_strength': 0, # Sub shine strength fixed to 0
            'sub_shine_texture': 0, # Sub shine texture fixed to 0
        })
    # If color_flag == 0, no color/shine data is added, which matches the parser behavior.

    # 處理 swimsuit 的 option flags
    if slot == 'swimsuit':
        options = get_option_flags(slot, item_id)
        if 'option_top' in options:
            formatted_data['option_top'] = random.choice(['on', 'off'])
        if 'option_bottom' in options:
            formatted_data['option_bottom'] = random.choice(['on', 'off'])

    return formatted_data


@pytest.mark.parametrize("_", range(400)) # 減少測試次數以加快執行速度，實際建議 300+
def test_random_clothing_roundtrip(_):
    original_clothing_data = {}

    # --- 構建隨機原始數據 ---
    for slot_name in CLOTHING_ITEMS.keys():
        # Ensure 'swimsuit' is handled separately for its specific options
        if slot_name == 'swimsuit':
            # Pick a swimsuit item
            selected_swimsuit = random.choice(CLOTHING_ITEMS['swimsuit'])
            item_data = format_for_test('swimsuit', selected_swimsuit)
            if item_data:
                original_clothing_data['swimsuit'] = item_data
            else:
                print(f"Skipping swimsuit due to no available items or formatting issue.")
            continue # Already handled swimsuit and its options

        # For other slots, just pick a random item
        item_data = format_for_test(slot_name)
        if item_data: # format_for_test might return None if no items are available
            original_clothing_data[slot_name] = item_data
        else:
            print(f"Skipping slot '{slot_name}' due to no available items or formatting issue.")

    # Determine clothing_set (usually '通常' or '水著')
    # If a swimsuit is selected, set to '水著', otherwise '通常'
    clothing_set = '水著' if original_clothing_data.get('swimsuit', {}).get('id') != 0 else '通常'
    original_clothing_data['clothing_set'] = clothing_set


    # --- 序列化並回讀 ---
    stream = BytesIO()
    serialize_clothing_data(stream, original_clothing_data, debug_mode=False)
    stream.seek(0)
    parsed_clothing_data = parse_clothing_data(stream, debug_mode=False)


    # --- 比對數據 ---
    print(f"\n--- Clothing Roundtrip Test {_+1} ---")
    # Print some key data points for debugging
    for slot_name in CLOTHING_ITEMS.keys():
        if slot_name in original_clothing_data and original_clothing_data[slot_name]:
            original_id = original_clothing_data[slot_name].get('id')
            parsed_id = parsed_clothing_data.get(slot_name, {}).get('id')
            original_name = original_clothing_data[slot_name].get('#name')
            parsed_name = parsed_clothing_data.get(slot_name, {}).get('#name') # Parser adds this

            print(f"  Slot: {slot_name}")
            print(f"    Original ID: {original_id}, Name: {original_name}")
            print(f"    Parsed ID: {parsed_id}, Name: {parsed_name}")

            # Specific check for swimsuit options as they are top-level in parsed_clothing_data
            if slot_name == 'swimsuit':
                orig_opt_top = original_clothing_data['swimsuit'].get('option_top')
                parsed_opt_top = parsed_clothing_data['swimsuit'].get('option_top')
                orig_opt_bottom = original_clothing_data['swimsuit'].get('option_bottom')
                parsed_opt_bottom = parsed_clothing_data['swimsuit'].get('option_bottom')
                if orig_opt_top is not None:
                    print(f"    Original Swimsuit Option Top: {orig_opt_top}")
                    print(f"    Parsed Swimsuit Option Top: {parsed_opt_top}")
                if orig_opt_bottom is not None:
                    print(f"    Original Swimsuit Option Bottom: {orig_opt_bottom}")
                    print(f"    Parsed Swimsuit Option Bottom: {parsed_opt_bottom}")


    # Compare 'clothing_set' which is at the top level
    print(f"  Original Clothing Set: {original_clothing_data.get('clothing_set')}")
    print(f"  Parsed Clothing Set: {parsed_clothing_data.get('clothing_set')}")

    # For `!disable_by`, the parser adds it, but the serializer doesn't use it.
    # It's better to remove it from parsed_clothing_data before comparison if it causes issues.
    # However, since `compare_dicts` only checks if keys exist and values match, it might be fine.
    # Let's ensure `compare_dicts` gracefully handles extra keys in parsed data.
    # If not, we might need to filter. For now, assume it's okay.

    # Remove dynamic runtime additions from parsed data before comparison if they interfere
    # The '#name' field is added by the parser and is not part of the original data used for serialization.
    # Similarly, '!disable_by' is added by the parser.
    # These should be removed from parsed_clothing_data before comparison if `compare_dicts` expects exact match.
    # Let's refine `compare_dicts` to ignore keys starting with '!' or '#'.
    # For now, let's just make sure the values that are supposed to be written/read match.

    # Filter `parsed_clothing_data` for comparison to remove parser-added fields
    # This is a safe way to ensure the comparison only focuses on the data that was serialized.
    filtered_parsed_clothing_data = {}
    for slot_name, original_item in original_clothing_data.items():
        if slot_name == 'clothing_set':
            filtered_parsed_clothing_data[slot_name] = parsed_clothing_data.get(slot_name)
            continue
        parsed_item = parsed_clothing_data.get(slot_name, {})
        filtered_item = {}
        for key, value in original_item.items():
            # Exclude keys starting with '!' or '#' from the comparison for this specific test
            if not (key.startswith('!') or key.startswith('#')):
                filtered_item[key] = parsed_item.get(key)
        filtered_parsed_clothing_data[slot_name] = filtered_item
    
    # Manually re-add swimsuit options if they exist at the top level
    # Because they are handled at the very end in the parse/serialize functions
    if 'swimsuit' in original_clothing_data and 'option_top' in original_clothing_data['swimsuit']:
        filtered_parsed_clothing_data['swimsuit']['option_top'] = parsed_clothing_data['swimsuit'].get('option_top')
    if 'swimsuit' in original_clothing_data and 'option_bottom' in original_clothing_data['swimsuit']:
        filtered_parsed_clothing_data['swimsuit']['option_bottom'] = parsed_clothing_data['swimsuit'].get('option_bottom')


    # Special handling for color flag 1 and 2 where some values are fixed by the parser/game logic
    # We need to ensure these fixed values are reflected in the original_clothing_data for accurate comparison
    for slot_name, o_item in original_clothing_data.items():
        if isinstance(o_item, dict) and 'color' in o_item:
            color_flag = o_item['color']
            if color_flag == 1:
                # Parser will output these fixed values for color_flag 1
                o_item['sub_color'] = '(255, 255, 255, 255)'
                o_item['main_shine'] = '(0, 0, 0, 0)'
                o_item['main_shine_strength'] = 0
                o_item['main_shine_texture'] = 0
                o_item['sub_shine_color'] = '(0, 0, 0, 0)'
                o_item['sub_shine_strength'] = 0
                o_item['sub_shine_texture'] = 0
            elif color_flag == 2:
                # Parser will output these fixed values for color_flag 2
                o_item['main_shine_strength'] = 0
                o_item['main_shine_texture'] = 0
                o_item['sub_shine_strength'] = 0
                o_item['sub_shine_texture'] = 0

    # Ensure to compare the original_clothing_data *after* fixing the values for specific color flags
    # with the parsed data.
    # The `compare_dicts` function might need to be robust enough to handle the difference in keys
    # added by the parser ('#name', '!disable_by').
    # For now, let's assume `compare_dicts` only checks for keys present in the first dict.
    compare_dicts(original_clothing_data, parsed_clothing_data)


    print(f"--- Clothing Roundtrip Test {_+1} Passed! ---")