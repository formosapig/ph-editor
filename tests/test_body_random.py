# ph-editor/tests/test_body_random.py

import random
from io import BytesIO

import pytest

# test utils
from tests.utils import compare_dicts, _random_color_str, _random_hex_string
# 導入序列化和解析函數
from serializers.body_serializer import serialize_body_data
from parsers.body_parser import parse_body_data
from game_data.body_data import BODY_DETAILS

def format_for_test(category_name: str, item: dict = None):
    """
    構建用於序列化測試的 body_data 結構的一個部分。
    會填充隨機或預設的數值、顏色值。
    """
    formatted_data = {}

    # 針對不同的 category_name 填充數據
    if category_name == 'overall':
        # skin_id 來自 BODY_DETAILS['skin']
        selected_skin = item if item else random.choice(BODY_DETAILS['skin'])
        formatted_data = {
            "skin_id": selected_skin['id'],
            "skin_extra": 5, # 固定值
            "hue": random.randint(-50, 50),
            "saturation": random.randint(0, 100),
            "value": random.randint(0, 100),
            "!alpha": random.randint(0, 100),
            "gloss_strength": random.randint(0, 100),
            "gloss_texture": random.randint(0, 100),
            "!extra_value2": _random_hex_string(4),
            "flesh_strength": random.randint(0, 100),
            "height": random.randint(0, 100), # 獨立寫入，但屬於 overall
            "head_size": random.randint(0, 100), # 獨立寫入，但屬於 overall
        }
    elif category_name == 'pubic_hair':
        selected_ph = item if item else random.choice(BODY_DETAILS['pubic_hair'])
        formatted_data = {
            "id": selected_ph['id'],
            "extra": 4, # 固定值
            "color": _random_color_str(),
            "!strength": random.randint(0, 100),
            "!texture": random.randint(0, 100),
        }
    elif category_name == 'tattoo':
        selected_tattoo = item if item else random.choice(BODY_DETAILS['tattoo'])
        formatted_data = {
            "id": selected_tattoo['id'],
            "color": _random_color_str(),
            "!padding1": _random_hex_string(4), # 4 bytes padding
        }
    elif category_name == 'breast':
        # 胸部尺寸相關的浮點數
        formatted_data = {
            "size": random.randint(0, 100),
            "vertical_position": random.randint(0, 100),
            "horizontal_spread": random.randint(0, 100),
            "horizontal_position": random.randint(0, 100),
            "angle": random.randint(0, 100),
            "firmness": random.randint(0, 100),
            "areola_prominence": random.randint(0, 100),
            "nipple_thickness": random.randint(0, 100),
            "nipple_erectness": random.randint(0, 100), # 獨立寫入，但屬於 breast
            "softness": random.randint(0, 100), # 獨立寫入，但屬於 breast
            "weight": random.randint(0, 100), # 獨立寫入，但屬於 breast
        }
    elif category_name == 'nipples':
        # nipples 屬於 breast 的子項目，但有自己的 ID 和顏色參數
        # 在 body_data 的結構中，nipples 會是 breast 的一個子字典
        selected_nipple_type = item if item else random.choice(BODY_DETAILS['nipples'])
        formatted_data = {
            "id": selected_nipple_type['id'],
            "extra": 5, # 固定值
            "hue": random.randint(-50, 50),
            "saturation": random.randint(0, 100),
            "value": random.randint(0, 100),
            "alpha": random.randint(0, 100),
            "gloss_strength": random.randint(0, 100),
            "gloss_texture": random.randint(0, 100),
            "areola_size": random.randint(0, 100), # 獨立寫入，但屬於 nipples
        }
    elif category_name == 'upper_body':
        formatted_data = {
            "neck_width": random.randint(0, 100),
            "neck_thickness": random.randint(0, 100),
            "torso_shoulder_width": random.randint(0, 100),
            "torso_shoulder_thickness": random.randint(0, 100),
            "torso_upper_width": random.randint(0, 100),
            "torso_upper_thickness": random.randint(0, 100),
            "torso_lower_width": random.randint(0, 100),
            "torso_lower_thickness": random.randint(0, 100),
        }
    elif category_name == 'lower_body':
        formatted_data = {
            "waist_position": random.randint(0, 100),
            "waist_upper_width": random.randint(0, 100),
            "waist_upper_thickness": random.randint(0, 100),
            "waist_lower_width": random.randint(0, 100),
            "waist_lower_thickness": random.randint(0, 100),
            "hip_size": random.randint(0, 100),
            "hip_angle": random.randint(0, 100),
        }
    elif category_name == 'legs':
        formatted_data = {
            "thigh_upper": random.randint(0, 100),
            "thigh_lower": random.randint(0, 100),
            "calf": random.randint(0, 100),
            "ankle": random.randint(0, 100),
        }
    elif category_name == 'arms':
        formatted_data = {
            "shoulder": random.randint(0, 100),
            "upper_arm": random.randint(0, 100),
            "forearm": random.randint(0, 100),
        }
    elif category_name == 'tan_lines':
        selected_tan = item if item else random.choice(BODY_DETAILS['tan_lines'])
        formatted_data = {
            "id": selected_tan['id'],
            "hue": random.randint(-50, 50),
            "saturation": random.randint(0, 100),
            "value": random.randint(0, 100),
            "intensity": random.randint(0, 100),
            "!padding1": _random_hex_string(4), # 4 bytes padding
        }
    elif category_name == 'nails':
        formatted_data = {
            "hue": random.randint(-50, 50),
            "saturation": random.randint(0, 100),
            "value": random.randint(0, 100),
            "alpha": random.randint(0, 100),
            "gloss_strength": random.randint(0, 100),
            "gloss_texture": random.randint(0, 100),
            "!padding1": _random_hex_string(4), # 4 bytes padding
            "polish": { # 指甲油作為 nails 的子項目
                "color": _random_color_str(),
                "!shine": _random_color_str(),
                "shine_strength": random.randint(0, 100),
                "shine_texture": random.randint(0, 100),
            }
        }
    else:
        print(f"Warning: Unhandled category for test formatting: {category_name}")
        return {}

    # 添加一個名稱，因為解析器可能會讀取它，儘管序列化時可能不會寫入
    if item and 'id' in item and 'name' in item:
        # 對於具有 ID 和 name 的項目 (如 skin, pubic_hair, tattoo 等)
        if isinstance(item['id'], tuple):
            formatted_data["#name"] = item['name']['ja'] # 或 zh
        else:
            # 對於 int ID 的項目，解析器可能只返回 ID，所以 #name 可能不存在
            # 但如果解析器有邏輯將 ID 映射回名稱，則應包含
            pass

    return formatted_data


@pytest.mark.parametrize("_", range(300)) # 建議 300 次測試，確保足夠覆蓋
def test_random_body_roundtrip(_):
    original_body_data = {}

    # --- 構建隨機原始數據 ---
    # Overall Skin
    selected_skin = random.choice(BODY_DETAILS['skin'])
    original_body_data['overall'] = format_for_test('overall', selected_skin)

    # Pubic Hair
    selected_ph = random.choice(BODY_DETAILS['pubic_hair'])
    original_body_data['pubic_hair'] = format_for_test('pubic_hair', selected_ph)

    # Tattoo
    selected_tattoo = random.choice(BODY_DETAILS['tattoo'])
    original_body_data['tattoo'] = format_for_test('tattoo', selected_tattoo)

    # Chest / Breast
    original_body_data['breast'] = format_for_test('breast')
    # Nipples (作為 breast 的子字典)
    selected_nipple_type = random.choice(BODY_DETAILS['nipples'])
    original_body_data['breast']['nipples'] = format_for_test('nipples', selected_nipple_type)


    # Upper Body
    original_body_data['upper_body'] = format_for_test('upper_body')

    # Lower Body
    original_body_data['lower_body'] = format_for_test('lower_body')

    # Legs
    original_body_data['legs'] = format_for_test('legs')

    # Arms
    original_body_data['arms'] = format_for_test('arms')

    # Tan Lines
    selected_tan = random.choice(BODY_DETAILS['tan_lines'])
    original_body_data['tan_lines'] = format_for_test('tan_lines', selected_tan)

    # Nails (包含 Nail Polish 子項目)
    original_body_data['nails'] = format_for_test('nails')


    # --- 序列化並回讀 ---
    stream = BytesIO()
    # 注意：這裡 serialize_body_data 預期 debug_mode 參數，所以傳入 False
    serialize_body_data(original_body_data, stream)
    stream.seek(0)
    parsed_body_data = parse_body_data(stream) # 假設 parse_body_data 不接受 debug_mode


    # --- 比對數據 ---
    print(f"\n--- Roundtrip Test {_+1} ---")
    # 打印一些關鍵數據點以便於除錯
    print(f"  Original Skin ID: {original_body_data['overall']['skin_id']}")
    print(f"  Parsed Skin ID: {parsed_body_data['overall']['skin_id']}")
    print(f"  Original Pubic Hair ID: {original_body_data['pubic_hair']['id']}")
    print(f"  Parsed Pubic Hair ID: {parsed_body_data['pubic_hair']['id']}")
    print(f"  Original Nipple ID: {original_body_data['breast']['nipples']['id']}")
    print(f"  Parsed Nipple ID: {parsed_body_data['breast']['nipples']['id']}")

    # 開始遞歸比較
    compare_dicts(original_body_data, parsed_body_data)

    print(f"--- Roundtrip Test {_+1} Passed! ---")