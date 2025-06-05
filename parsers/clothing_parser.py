# your_character_project/parsers/clothing_parser.py

from io import BytesIO
import json
from common_types import (
    _read_uint32, _read_float, _read_color, format_color_for_json, _read_bytes_as_hex
)
# clothing data
from game_data.clothing_data import get_clothing_by_id, is_colorful

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
    slotIdx = _read_bytes_as_hex(stream, 4)
    item_id = (_read_uint32(stream), _read_uint32(stream))
    
    part = {
        'slot': slotIdx,
        'id': f"({item_id[0]}, {item_id[1]})",
        '#name': get_clothing_by_id(slot, item_id), 
    }

    # 可換色時...
    if is_colorful(slot, item_id) > 0:
        part.update(
            {
                # 主色
                'main_color': format_color_for_json(_read_color(stream)),
                # 主色光澤
                'main_shine': format_color_for_json(_read_color(stream)),
                'main_shine_strength': _format_float_to_percentage(_read_float(stream)),
                'main_shine_texture': _format_float_to_percentage(_read_float(stream)),

                # 輔色
                'sub_color': format_color_for_json(_read_color(stream)),
                # 輔色光澤
                'sub_shine_color': format_color_for_json(_read_color(stream)),
                'sub_shine_strength': _format_float_to_percentage(_read_float(stream)),
                'sub_shine_texture': _format_float_to_percentage(_read_float(stream)),
            }
        )
    # 最後分隔符?
    #part['end_mark'] = _read_bytes_as_hex(stream, 4)
  
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
    clothing_data = {}

    if debug_mode:
        current_pos = stream.tell()
        print(f"  [Offset: {current_pos}] Starting to parse clothing data.")

    try:
        # 上衣 (top)
        # 定位到 0x04BE
        #stream.seek(0x04BE)
        clothing_data['top'] = parse_clothing_item(stream, "top", debug_mode)
        if debug_mode: print(f"    [Offset: {stream.tell()}] End of Top data. Expected padding at 0x0516.")
        #_ = _read_uint32(stream) # 0x0516 padding

        # 下著 (bottom)
        # 定位到 0x051A
        #stream.seek(0x051A)
        clothing_data['bottom'] = parse_clothing_item(stream, "bottom", debug_mode)
        if debug_mode: print(f"    [Offset: {stream.tell()}] End of Bottom data. Expected padding at 0x0572.")
        #_ = _read_uint32(stream) # 0x0572 padding

        # 胸罩 (bra)
        # 定位到 0x0576
        #stream.seek(0x0576)
        clothing_data['bra'] = parse_clothing_item(stream, "bra", debug_mode)
        if debug_mode: print(f"    [Offset: {stream.tell()}] End of Bra data. Expected padding at 0x05CE.")
        #_ = _read_uint32(stream) # 0x05CE padding

        # 內褲 (panty)
        # 定位到 0x05D2
        #stream.seek(0x05D2)
        clothing_data['panty'] = parse_clothing_item(stream, "panty", debug_mode)
        if debug_mode: print(f"    [Offset: {stream.tell()}] End of Panty data. Expected padding at 0x062A.")
        #_ = _read_uint32(stream) # 0x062A padding

        # 泳裝 (swimsuit - full)
        # 定位到 0x062E
        #stream.seek(0x062E)
        clothing_data['swimsuit'] = parse_clothing_item(stream, "swimsuit", debug_mode)
        if debug_mode: print(f"    [Offset: {stream.tell()}] End of Swimsuit (Full) data. Expected padding at 0x0686.")
        #_ = _read_uint32(stream) # 0x0686 padding

        # 泳裝 - 上衣 (swimsuit - top 1)
        # 定位到 0x068A
        #stream.seek(0x068A)
        clothing_data['swimsuit_top'] = parse_clothing_item(stream, "swimsuit_top", debug_mode)
        if debug_mode: print(f"    [Offset: {stream.tell()}] End of Swimsuit Top 1 data. Expected padding at 0x06E2.")
        #_ = _read_uint32(stream) # 0x06E2 padding

        # 泳裝 - 上衣 (swimsuit - top 2)
        # 定位到 0x06E6
        #stream.seek(0x06E6)
        clothing_data['swimsuit_bottom'] = parse_clothing_item(stream, "swimsuit_bottom", debug_mode)
        if debug_mode: print(f"    [Offset: {stream.tell()}] End of Swimsuit Top 2 data. Expected padding at 0x073E.")
        #_ = _read_uint32(stream) # 0x073E padding

        # 手套 (gloves)
        # 定位到 0x0742
        #stream.seek(0x0742)
        clothing_data['gloves'] = parse_clothing_item(stream, "gloves", debug_mode)
        if debug_mode: print(f"    [Offset: {stream.tell()}] End of Gloves data. Expected padding at 0x079A.")
        #_ = _read_uint32(stream) # 0x079A padding

        # 褲襪 (pantyhose)
        # 定位到 0x079E
        #stream.seek(0x079E)
        clothing_data['pantyhose'] = parse_clothing_item(stream, "pantyhose", debug_mode)
        if debug_mode: print(f"    [Offset: {stream.tell()}] End of Pantyhose data. Expected padding at 0x07F6.")
        #_ = _read_uint32(stream) # 0x07F6 padding

        # 襪子 (socks)
        # 定位到 0x07FA
        #stream.seek(0x07FA)
        clothing_data['socks'] = parse_clothing_item(stream, "socks", debug_mode)
        if debug_mode: print(f"    [Offset: {stream.tell()}] End of Socks data. Expected padding at 0x0852.")
        #_ = _read_uint32(stream) # 0x0852 padding

        # 鞋子 (shoes)
        # 定位到 0x0856
        #stream.seek(0x0856)
        clothing_data['shoes'] = parse_clothing_item(stream, "shoes", debug_mode)
        if debug_mode: print(f"    [Offset: {stream.tell()}] End of Shoes data.")
        # 最後的 padding 0x08AE 沒有明確說明，這裡不讀取

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