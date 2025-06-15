# your_character_project/serializers/hair_serializer.py

from io import BytesIO
from common_types import (
    _pack_bytes, _pack_uint16, _pack_uint32, _pack_float, _pack_int32, _pack_color
)

def _serialize_single_hair_part(stream: BytesIO, part_data: dict, part_name: str):
    print(f"    開始序列化 {part_name} 髮型部件...")

    # 1. 髮型 ID（兩個 int32）
    hair_id = part_data.get('id', '(0,0)').strip('()').split(',')
    stream.write(_pack_int32(int(hair_id[0])))
    stream.write(_pack_int32(int(hair_id[1])))

    # 2. 色彩與光澤資料
    stream.write(_pack_color(part_data['color']))
    stream.write(_pack_color(part_data['shine1_color']))
    stream.write(_pack_float(part_data.get('shine1_effect', 0) / 5.0))
    stream.write(_pack_color(part_data['shine2_color']))
    stream.write(_pack_float(part_data.get('shine2_effect', 0) / 12.5))

    # 3. 配飾資料
    if 'accessory' in part_data:
        stream.write(bytes.fromhex(part_data.get('accessory_mark', '00000000')))
        accessory = part_data['accessory']
        stream.write(_pack_color(accessory['color']))
        stream.write(_pack_color(accessory['shine_color']))
        stream.write(_pack_float(accessory.get('shine_strength', 0) / 100.0))
        stream.write(_pack_float(accessory.get('shine_texture', 0) / 100.0))
    else:
        stream.write(bytes.fromhex(part_data.get('end_mark', '00000000')))

    print(f"    完成 {part_name} 髮型部件的序列化。")

def serialize_hair_data(hair_data: dict, stream: BytesIO):
    """
    序列化髮型數據，支援 back_hair, front_hair, side_hair。
    """
    current_pos = stream.tell()
    print(f"    [偏移: {current_pos}] 開始序列化所有髮型數據。")

    _serialize_single_hair_part(stream, hair_data['back_hair'], 'back_hair')
    _serialize_single_hair_part(stream, hair_data['front_hair'], 'front_hair')
    _serialize_single_hair_part(stream, hair_data['side_hair'], 'side_hair')

    print(f"    髮型數據序列化完成。下一個寫入位置: {stream.tell()}")
