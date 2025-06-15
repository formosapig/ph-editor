# your_flask_app/parsers/hair_parser.py

from io import BytesIO
from common_types import (
    _read_uint32, _read_uint8, _read_float, _read_bytes,
    _read_color, _format_color_for_json, _read_uint16,
    _read_bytes_as_hex, _read_int32
)
import json
from game_data.hair_data import get_hair_by_id, has_accessory, is_set


def _parse_single_hair_part(stream: BytesIO, part_name: str, debug_mode: bool = False) -> dict:
    """
    解析單一髮型部件的數據（例如：Set髮/後髮、側髮、前髮）。
    此函式將獨立讀取並返回一個髮型部件的所有標準數據。
    """
    part_data = {}

    try:
        # 髮型的編碼...
        hair_id = (_read_int32(stream), _read_int32(stream))
        part_data['id'] = f"({hair_id[0]}, {hair_id[1]})"
        
        # 是整套的髮型?
        if is_set(part_name, hair_id):
            part_data['#set'] = True
            
        # 這邊不讀檔, 讀取 hair 的名稱
        part_data['#name'] = get_hair_by_id(part_name, hair_id)        

        part_data['color'] = _format_color_for_json(_read_color(stream))
        part_data['shine1_color'] = _format_color_for_json(_read_color(stream))
        # 「ツヤ絞り」＝「光澤絞紋值」 或 「光澤皺紋程度」
        part_data['shine1_effect'] = max(0, min(100, round(_read_float(stream) * 5))) 
 
        part_data['shine2_color'] = _format_color_for_json(_read_color(stream))
        # 「ツヤ絞り」＝「光澤絞紋值」 或 「光澤皺紋程度」
        part_data['shine2_effect'] = max(0, min(100, round(_read_float(stream) * 12.5))) 
            
        # 取得髮型是否有配飾的資料...
        if has_accessory(part_name, hair_id):
        
            # 4 個 bytes 應該是配飾專屬標記 b'\x02\x00\x00\x00' = ACCESSORY_MARK
            part_data['accessory_mark'] = _read_bytes_as_hex(stream, 4)
        
            accessory_data = {
                'color': _format_color_for_json(_read_color(stream)),
                'shine_color': _format_color_for_json(_read_color(stream)),
                'shine_strength': max(0, min(100, round(_read_float(stream) * 100))),
                'shine_texture': max(0, min(100, round(_read_float(stream) * 100))),
            }            
        
            # 將配飾物件放入 part_data
            part_data['accessory'] = accessory_data         
        
        else:
            # 沒有配飾時, 最後 4 個 bytes 應該是本髮型結尾 b'\x00\x00\x00\x00' = END_MARK
            part_data['end_mark'] = _read_bytes_as_hex(stream, 4)

        
    except EOFError as e:
        if debug_mode:
            print(f"    [ERROR] Stream ended prematurely when parsing {part_name} data: {e}")
        raise 
    except Exception as e:
        if debug_mode:
            print(f"    [ERROR] Unknown error occurred when parsing {part_name} data: {e}")
        raise 
        
    return part_data


def parse_hair_data(stream: BytesIO, debug_mode: bool = False) -> dict:
    """
    解析角色的所有髮型數據部件。
    不管遊戲中是否使用，所有部件的數據都會被解析並儲存。
    """
    all_hair_data = {}
    current_pos = stream.tell()
    if debug_mode:
        print(f"  [Offset: {current_pos}] Starting to parse all hair data parts.")

    try:
        # 1. 解析 Set/Back Hair (Set髮/後髮) 部分
        all_hair_data['back_hair'] = _parse_single_hair_part(stream, 'back', debug_mode)
        
        # 2. 解析 Front Hair (前髮) 部分
        all_hair_data['front_hair'] = _parse_single_hair_part(stream, 'front', debug_mode)

        # 3. 解析 Side Hair (側髮) 部分
        all_hair_data['side_hair'] = _parse_single_hair_part(stream, 'side', debug_mode)

    except EOFError as e:
        if debug_mode:
            print(f"  [ERROR] Stream ended prematurely when parsing total hair data: {e}")
        raise 
    except Exception as e:
        if debug_mode:
            print(f"  [ERROR] Unknown error occurred when parsing total hair data: {e}")
        raise 

    if debug_mode:
        print(f"  All hair data parts parsing complete. Next read position: {stream.tell()}")
        try:
            json_output = json.dumps(all_hair_data, indent=2, ensure_ascii=False)
            print("\n  --- Hair Parser JSON Debug Output ---")
            print(json_output)
            print("  -----------------------------------\n")
        except TypeError as json_e:
            print(f"\n  [CRITICAL ERROR] Hair parser returned data cannot be JSON serialized: {json_e}")
            problematic_types = []
            def find_bytes_in_dict(d):
                for k, v in d.items():
                    if isinstance(v, (bytes, bytearray)):
                        problematic_types.append(f"Key '{k}': {type(v)}")
                    elif isinstance(v, dict):
                        find_bytes_in_dict(v)
            find_bytes_in_dict(all_hair_data)
            print(f"  Unserializable data types: {problematic_types}")
            print("  -----------------------------------\n")
        
    return all_hair_data