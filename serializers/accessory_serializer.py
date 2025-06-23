# ph-editor/serializers/accessory_serializer.py

from io import BytesIO
from utils.common_types import (
    _pack_int32, _pack_float, _pack_color, _pack_hex_to_bytes,
    _parse_and_pack_float
)

def serialize_accessory_item(accessory_item_data: dict, stream: BytesIO, debug_mode: bool = False):
    """
    將單一配飾的數據字典序列化回 BytesIO 二進位資料。
    Args:
        accessory_item_data: 包含單一配飾數據的字典。
        stream: 要寫入二進位資料的 BytesIO 串流物件。
        debug_mode: 是否開啟除錯模式，印出詳細序列化過程。
    """
    start_offset = stream.tell()
    if debug_mode:
        print(f"    [Offset: {start_offset}] Starting to serialize accessory item.")

    # 序列化基本屬性
    stream.write(_pack_int32(accessory_item_data.get('type', -1))) # -1 = 無
    stream.write(_pack_int32(accessory_item_data.get('id', 0)))
    stream.write(_pack_int32(accessory_item_data.get('slot', 0)))

    # 序列化位置 (position)
    position = accessory_item_data.get('position', {'x': 0.0, 'y': 0.0, 'z': 0.0})
    stream.write(_pack_float(position.get('x', 0.0)))
    stream.write(_pack_float(position.get('y', 0.0)))
    stream.write(_pack_float(position.get('z', 0.0)))

    # 序列化旋轉 (rotation)
    rotation = accessory_item_data.get('rotation', {'x': 0.0, 'y': 0.0, 'z': 0.0})
    stream.write(_pack_float(rotation.get('x', 0.0)))
    stream.write(_pack_float(rotation.get('y', 0.0)))
    stream.write(_pack_float(rotation.get('z', 0.0)))

    # 序列化縮放 (scale)
    scale = accessory_item_data.get('scale', {'x': 0.0, 'y': 0.0, 'z': 0.0})
    stream.write(_pack_float(scale.get('x', 0.0)))
    stream.write(_pack_float(scale.get('y', 0.0)))
    stream.write(_pack_float(scale.get('z', 0.0)))

    # 序列化 !color_mark
    color_mark = accessory_item_data.get('!color_mark', "00 00 00 00")
    stream.write(_pack_hex_to_bytes(color_mark, 4))

    # 根據 !color_mark 序列化顏色和光澤屬性
    if color_mark == '03 00 00 00':
        if debug_mode:
            print(f"    [Offset: {stream.tell()}] Serializing colorful accessory properties.")
        stream.write(_pack_color(accessory_item_data.get('main_color', "(255, 255, 255, 255)")))
        stream.write(_pack_color(accessory_item_data.get('main_shine', "(255, 255, 255, 255)")))
        # Note: _parse_and_pack_float uses default scale=100, min_val=0, max_val=100
        # which matches _read_and_format_to_value's defaults used for these fields.
        stream.write(_parse_and_pack_float(accessory_item_data.get('main_strength', 0)))
        stream.write(_parse_and_pack_float(accessory_item_data.get('main_texture', 0)))

        stream.write(_pack_color(accessory_item_data.get('sub_color', "(255, 255, 255, 255)")))
        stream.write(_pack_color(accessory_item_data.get('sub_shine', "(255, 255, 255, 255)")))
        stream.write(_parse_and_pack_float(accessory_item_data.get('sub_strength', 0)))
        stream.write(_parse_and_pack_float(accessory_item_data.get('sub_texture', 0)))
    else:
        if debug_mode:
            print(f"    [Offset: {stream.tell()}] No colorful accessory properties to serialize (color_mark: {color_mark}).")

    if debug_mode:
        print(f"    [Offset: {stream.tell()}] Finished serializing accessory item.")

def serialize_accessories_data(accessories_data: dict, stream: BytesIO, debug_mode: bool = False):
    """
    將 parse_accessories_data 生成的 accessories_data dict 序列化回 BytesIO 二進位資料。
    使用 _pack_* 系列函式來轉換並寫入。

    Args:
        accessories_data: 包含配飾數據的字典，格式應與 parse_accessories_data 的輸出一致。
        stream: 要寫入二進位資料的 BytesIO 串流物件。
        debug_mode: 是否開啟除錯模式，印出詳細序列化過程。
    """
    current_pos = stream.tell()
    if debug_mode:
        print(f"  [Offset: {current_pos}] Starting to serialize accessories data.")

    try:
        # Loop through 10 accessory slots (accessory_01 to accessory_10)
        for i in range(1, 11): # Loop from 1 to 10
            accessory_key = f'accessory_{i:02}'
            if accessory_key in accessories_data:
                serialize_accessory_item(accessories_data[accessory_key], stream, debug_mode)
            else:
                # If an accessory key is missing, write default (empty) accessory data
                if debug_mode:
                    print(f"    [WARNING] Missing accessory data for {accessory_key}. Writing default empty values.")
                serialize_accessory_item({}, stream, debug_mode) # Pass an empty dict to write defaults

    except Exception as e:
        if debug_mode:
            print(f"  [ERROR] An error occurred during accessories data serialization: {e}")
        raise
    finally:
        if debug_mode:
            print(f"  Accessories data serialization complete. Final stream position: {stream.tell()}")
