# your_character_project/parsers/accessory_parser.py

from io import BytesIO
import json
from common_types import (
    _read_uint8, _read_uint32, _read_int32, _read_float, _read_color, format_color_for_json, _read_bytes_as_hex
)
# accessory data
from game_data.accessory_data import get_accessory_by_id, is_colorful, ACCESSORY_SLOT_NAMES
import math


def _format_float_to_percentage(value: float | None, scale: float = 100, debug_mode: bool = False) -> int:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        value = 0.0

    percentage = round(value * scale)
    
    if debug_mode:
        if percentage < 0 or percentage > 100:
            print(f"    [WARN] Value {value} resulted in {percentage}%, clamped to [0, 100].")
    
    return max(0, min(100, percentage))

def parse_accessory_item(stream: BytesIO, slot_index: int, debug_mode: bool = False) -> dict:
    """
    解析單一配飾的數據，包括 ID、顏色和光澤屬性。
    Args:
        stream: 包含角色二進位資料的 BytesIO 串流物件。
        slot_index: 當前解析的配飾槽位索引 (0-9)，用於除錯輸出。
        debug_mode: 是否開啟除錯模式，印出詳細解析過程。
    Returns:
        一個字典，包含解析後的配飾數據。
    """
    start_offset = stream.tell()
    # 使用 ACCESSORY_SLOT_NAMES 來取得中文名稱，用於除錯輸出
    slot_display_name = ACCESSORY_SLOT_NAMES[slot_index] if slot_index < len(ACCESSORY_SLOT_NAMES) else f"未知槽位 {slot_index}"
    
    if debug_mode:
        print(f"    [Offset: {start_offset}] Parsing accessory item for slot {slot_index} ('{slot_display_name}').")

    # 輔助函式，用於處理可能是 NaN 的浮點數
    def _read_and_handle_float(s: BytesIO, name: str) -> float | None:
        val = _read_float(s)
        if val != val: # Check for NaN
            if debug_mode:
                print(f"      [WARN] Read NaN for {name} in slot {slot_index}. Converting to None for JSON.")
            return None
        return val
        
    # 讀取基本屬性
    #accessory_type = _read_uint32(stream)
    accessory_id_tuple = (_read_int32(stream), _read_int32(stream))    
    #head = _read_bytes_as_hex(stream, 8)
    equip_position = _read_int32(stream)

    part = {
        'type': "???",
        'id': f"({accessory_id_tuple[0]}, {accessory_id_tuple[1]})",
        '#name': get_accessory_by_id(accessory_id_tuple), # 使用 item_id_tuple 傳遞
        'equip_position': equip_position,
        'position_adjust': {
                'x': _read_and_handle_float(stream, 'position_adjust_x'),
                'y': _read_and_handle_float(stream, 'position_adjust_y'),
                'z': _read_and_handle_float(stream, 'position_adjust_z')
            },
            'rotation_adjust': {
                'x': _read_and_handle_float(stream, 'rotation_adjust_x'),
                'y': _read_and_handle_float(stream, 'rotation_adjust_y'),
                'z': _read_and_handle_float(stream, 'rotation_adjust_z')
            },
            'scale_adjust': {
                'x': _read_and_handle_float(stream, 'scale_adjust_x'),
                'y': _read_and_handle_float(stream, 'scale_adjust_y'),
                'z': _read_and_handle_float(stream, 'scale_adjust_z')
            }
    }

    part['gap'] = _read_bytes_as_hex(stream, 4)
   
    # 讀取顏色和光澤屬性 (如果可換色)
    if is_colorful(accessory_id_tuple) > 0: 
        part.update(
            {
                'main_color': format_color_for_json(_read_color(stream)),
                'main_shine': format_color_for_json(_read_color(stream)),
                # 關鍵修改：使用 `or 0.0` 提供預設值
                'main_shine_strength': _format_float_to_percentage(_read_and_handle_float(stream, 'main_shine_strength') or 0.0), 
                'main_shine_texture': _format_float_to_percentage(_read_and_handle_float(stream, 'main_shine_texture') or 0.0), 

                'sub_color': format_color_for_json(_read_color(stream)),
                'sub_shine_color': format_color_for_json(_read_color(stream)),
                'sub_shine_strength': _format_float_to_percentage(_read_and_handle_float(stream, 'sub_shine_strength') or 0.0),
                'sub_shine_texture': _format_float_to_percentage(_read_and_handle_float(stream, 'sub_shine_texture') or 0.0),
            }
        )
    
            
    
    #part['align'] = _read_bytes_as_hex(stream, 5)
    
    if debug_mode:
        print(f"    [Offset: {stream.tell()}] Finished parsing accessory item for slot {slot_index}.")

    return part

def parse_accessories_data(stream: BytesIO, debug_mode: bool = False) -> dict:
    """
    解析角色的配飾數據。
    Args:
        stream: 包含角色二進位資料的 BytesIO 串流物件。
        debug_mode: 是否開啟除錯模式，印出詳細解析過程。
    Returns:
        一個字典，包含解析後的配飾數據和剩餘的位元組長度。
    """
    accessories_data = {}
    

    if debug_mode:
        current_pos = stream.tell()
        print(f"  [Offset: {current_pos}] Starting to parse accessories data.")
        print(f"  Expected single accessory block length: {SINGLE_ACCESSORY_BLOCK_LENGTH} bytes.")

    try:
        # 先讀取開頭的 4 bytes padding (0x08AE)
        # stream.seek(0x08AE) # 如果檔案開頭不是從這裡開始讀取，則需要seek
        #accessories_data['start'] = _read_bytes_as_hex(stream, 16) # 0x08AE padding
        if debug_mode: print(f"    [Offset: {stream.tell()}] Read 4 bytes padding after clothing data.")

        # 解析 10 個配飾槽位
        for i in range(10): # 10 個槽位，從 0 到 9
            accessories_data[f'accessory_{i+1:02}'] = parse_accessory_item(stream, i, debug_mode)

    except EOFError as e:
        if debug_mode:
            print(f"    [ERROR] Stream ended prematurely when parsing accessories data: {e}")
        raise
    except Exception as e:
        if debug_mode:
            print(f"    [ERROR] Unknown error occurred when parsing accessories data: {e}")
        raise
    finally:
        # 計算並儲存剩餘的位元組長度
        accessories_data['least_bytes'] = len(stream.getvalue()) - stream.tell()
        if debug_mode:
            print(f"  Accessories data parsing complete. Next read position: {stream.tell()}")
            print(f"  Least bytes remaining: {accessories_data['least_bytes']}")

            try:
                json_output = json.dumps(accessories_data, indent=2, ensure_ascii=False)
                print("\n  --- Accessories Parser JSON Debug Output ---")
                print(json_output)
                print("  -----------------------------------\n")
            except TypeError as json_e:
                print(f"\n  [CRITICAL ERROR] Accessories parser returned data cannot be JSON serialized: {json_e}")
                problematic_types = []
                def find_unserializable_in_dict(d):
                    for k, v in d.items():
                        if isinstance(v, (bytes, bytearray)):
                            problematic_types.append(f"Key '{k}': {type(v)}")
                        elif isinstance(v, dict):
                            find_unserializable_in_dict(v)
                find_unserializable_in_dict(accessories_data)
                print(f"  Unserializable data types: {problematic_types}")
                print("  -----------------------------------\n")

    return accessories_data