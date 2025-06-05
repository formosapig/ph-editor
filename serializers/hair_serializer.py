# your_character_project/serializers/hair_serializer.py

from io import BytesIO
from common_types import _pack_bytes, _pack_uint16, _pack_uint32, _pack_float

# 為了統一空殼長度，假設髮型數據區塊的預期最大長度
# 實際序列化時，你需要根據 hair_data['type_id'] 寫入不同長度
HAIR_DATA_MAX_LENGTH = 40 # 範例，請根據你實際格式的最大長度調整

def serialize_hair_data(hair_data: dict, stream: BytesIO):
    """
    序列化髮型數據。此為空殼實作。
    Args:
        hair_data: 包含髮型數據的字典。
        stream: BytesIO 串流物件，用於寫入位元組。
    """
    current_pos = stream.tell()
    print(f"    [偏移: {current_pos}] 開始序列化髮型數據 (空殼實作)。")

    # 實際實作時，你會根據 hair_data['type_id'] 寫入不同的數據
    # stream.write(_pack_uint16(hair_data.get('type_id', 0)))
    # stream.write(_pack_uint16(hair_data.get('active_value', 0)))
    # if hair_data.get('type_id') == 0:
    #     stream.write(_pack_uint32(hair_data.get('color', 0)))
    # ...

    # 空殼實作：填充固定長度的 0x00
    stream.write(_pack_bytes(b'\x00' * HAIR_DATA_MAX_LENGTH))

    print(f"    髮型數據序列化完成 (空殼實作)。下一個寫入位置: {stream.tell()}")