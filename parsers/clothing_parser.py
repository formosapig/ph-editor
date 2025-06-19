# ph-editor/parsers/clothing_parser.py

from io import BytesIO
import json
from common_types import (
    _read_uint32, _read_int32, _read_uint8, _read_float, _read_color, _format_color_for_json, _read_bytes_as_hex
)
# clothing data
from game_data.clothing_data import (
    get_clothing_by_id,
    is_colorful,
    is_disabled,
    is_cut_clothing,
    has_option,
    get_option_flags
)


# 全域部位禁用 dict
disable_dict = {}

# 從 body_parser.py 借用過來的浮點數轉換函式
def _format_float_to_percentage(value: float, scale: float = 100, debug_mode: bool = False) -> int:
    """
    將浮點數轉換為 0-100% 的整數值。
    """
    percentage = round(value * scale)
    if debug_mode:
        if percentage < 0 or percentage > 100:
            print(f"    [WARN] Value {value} resulted in {percentage}%, clamped to [0, 100].")
    return max(0, min(100, percentage))

def parse_clothing_item(stream: BytesIO, slot: str, debug_mode: bool = False) -> dict:
    """
    解析單一服裝配件的數據，包括 ID、顏色和光澤屬性。
    Args:
        stream: 包含角色二進位資料的 BytesIO 串流物件。
        debug_mode: 是否開啟除錯模式，印出詳細解析過程。
        item_name: 當前解析的服裝配件名稱，用於除錯輸出。
    Returns:
        一個字典，包含解析後的服裝數據。
    """
    if debug_mode:
        print(f"    [Offset: {stream.tell()}] Parsing '{item_name}' data.")

    # 讀取 ID 跟 extra, 並且取得名稱
    slotIdx = _read_int32(stream)
    item_id = _read_int32(stream)
    color_flag = _read_int32(stream)
    
    global disable_dict
    
    part = {
        'slot': slotIdx,
        'id': item_id,
        'color': color_flag,
        '#name': get_clothing_by_id(slot, item_id),
    }
            
    if slot in ('top', 'bottom') and is_cut_clothing(slot, item_id):
        part['#name'] += '[會穿模]'
    
    # 檢查禁用設定
    if slotIdx == 0: # top
        # 讀 option 確定 bottom, bra, panty 禁用
        disable_dict = {
            1: is_disabled('top', item_id, 'bottom'),
            2: is_disabled('top', item_id, 'bra'),
            3: is_disabled('top', item_id, 'panty'),
        }
        print(f"do slotIdx 0")
    else:
        if disable_dict.get(slotIdx, False):
            part['#disable_by'] = 'top'
            

    # 可換色時...
    # if is_colorful(slot, item_id) > 0:
    if color_flag == 3:
        part.update(
            {
                # 主色
                'main_color': _format_color_for_json(_read_color(stream)),
                # 主色光澤
                'main_shine': _format_color_for_json(_read_color(stream)),
                'main_shine_strength': _format_float_to_percentage(_read_float(stream)),
                'main_shine_texture': _format_float_to_percentage(_read_float(stream)),

                # 輔色
                'sub_color': _format_color_for_json(_read_color(stream)),
                # 輔色光澤
                'sub_shine_color': _format_color_for_json(_read_color(stream)),
                'sub_shine_strength': _format_float_to_percentage(_read_float(stream)),
                'sub_shine_texture': _format_float_to_percentage(_read_float(stream)),
            }
        )
  
    if slot == 'swimsuit':
        part.update(get_option_flags(slot, item_id)) 
  
    return part

def parse_clothing_data(stream: BytesIO, debug_mode: bool = False) -> dict:
    """
    解析角色的服裝數據。
    Args:
        stream: 包含角色二進位資料的 BytesIO 串流物件。
        debug_mode: 是否開啟除錯模式，印出詳細解析過程。
    Returns:
        一個字典，包含解析後的服裝數據。
    """
    clothing_data = {
        'clothing_set': None
    }

    if debug_mode:
        current_pos = stream.tell()
        print(f"  [Offset: {current_pos}] Starting to parse clothing data.")

    try:
        # 上衣 (top)
        clothing_data['top'] = parse_clothing_item(stream, "top", debug_mode)
        if debug_mode: print(f"    [Offset: {stream.tell()}] End of Top data. Expected padding at 0x0516.")

        # 下著 (bottom)
        clothing_data['bottom'] = parse_clothing_item(stream, "bottom", debug_mode)
        if debug_mode: print(f"    [Offset: {stream.tell()}] End of Bottom data. Expected padding at 0x0572.")

        # 胸罩 (bra)
        clothing_data['bra'] = parse_clothing_item(stream, "bra", debug_mode)
        if debug_mode: print(f"    [Offset: {stream.tell()}] End of Bra data. Expected padding at 0x05CE.")

        # 內褲 (panty)
        clothing_data['panty'] = parse_clothing_item(stream, "panty", debug_mode)
        if debug_mode: print(f"    [Offset: {stream.tell()}] End of Panty data. Expected padding at 0x062A.")

        # 泳裝 (swimsuit)
        clothing_data['swimsuit'] = parse_clothing_item(stream, "swimsuit", debug_mode)
        if debug_mode: print(f"    [Offset: {stream.tell()}] End of Swimsuit (Full) data. Expected padding at 0x0686.")

        # 泳裝 - 上衣 (swimsuit_top)
        clothing_data['swimsuit_top'] = parse_clothing_item(stream, "swimsuit_top", debug_mode)
        if debug_mode: print(f"    [Offset: {stream.tell()}] End of Swimsuit Top 1 data. Expected padding at 0x06E2.")

        # 泳裝 - 上衣 (swimsuit_bottom)
        clothing_data['swimsuit_bottom'] = parse_clothing_item(stream, "swimsuit_bottom", debug_mode)
        if debug_mode: print(f"    [Offset: {stream.tell()}] End of Swimsuit Top 2 data. Expected padding at 0x073E.")

        # 手套 (gloves)
        clothing_data['gloves'] = parse_clothing_item(stream, "gloves", debug_mode)
        if debug_mode: print(f"    [Offset: {stream.tell()}] End of Gloves data. Expected padding at 0x079A.")

        # 褲襪 (pantyhose)
        clothing_data['pantyhose'] = parse_clothing_item(stream, "pantyhose", debug_mode)
        if debug_mode: print(f"    [Offset: {stream.tell()}] End of Pantyhose data. Expected padding at 0x07F6.")

        # 襪子 (socks)
        clothing_data['socks'] = parse_clothing_item(stream, "socks", debug_mode)
        if debug_mode: print(f"    [Offset: {stream.tell()}] End of Socks data. Expected padding at 0x0852.")

        # 鞋子 (shoes)
        clothing_data['shoes'] = parse_clothing_item(stream, "shoes", debug_mode)
        if debug_mode: print(f"    [Offset: {stream.tell()}] End of Shoes data.")

        # 3 bytes always read...
        clothing_type = _read_uint8(stream)
        option_top = _read_uint8(stream)
        option_bottom = _read_uint8(stream)


        # 1 bytes
        # 0 = 通常衣服
        # 1 = 水著衣服
        clothing_data['clothing_set'] = '通常' if clothing_type == 0 else '水著'
        
        # 1 bytes 水著 Option 上
        # 0 = off
        # 1 = on
        if 'option_top' in clothing_data['swimsuit']:
            clothing_data['swimsuit']['option_top'] = 'on' if option_top == 1 else 'off'
        
        # 1 bytes 水著 option 下
        # 0 = off
        # 1 = on 
        if 'option_bottom' in clothing_data['swimsuit']:
            clothing_data['swimsuit']['option_bottom'] = 'on' if option_bottom == 1 else 'off'

    except EOFError as e:
        if debug_mode:
            print(f"    [ERROR] Stream ended prematurely when parsing clothing data: {e}")
        raise
    except Exception as e:
        if debug_mode:
            print(f"    [ERROR] Unknown error occurred when parsing clothing data: {e}")
        raise

    if debug_mode:
        print(f"  Clothing data parsing complete. Next read position: {stream.tell()}")
        try:
            json_output = json.dumps(clothing_data, indent=2, ensure_ascii=False)
            print("\n  --- Clothing Parser JSON Debug Output ---")
            print(json_output)
            print("  -----------------------------------\n")
        except TypeError as json_e:
            print(f"\n  [CRITICAL ERROR] Clothing parser returned data cannot be JSON serialized: {json_e}")
            problematic_types = []
            def find_unserializable_in_dict(d):
                for k, v in d.items():
                    if isinstance(v, (bytes, bytearray)):
                        problematic_types.append(f"Key '{k}': {type(v)}")
                    elif isinstance(v, dict):
                        find_unserializable_in_dict(v)
            find_unserializable_in_dict(clothing_data)
            print(f"  Unserializable data types: {problematic_types}")
            print("  -----------------------------------\n")

    return clothing_data