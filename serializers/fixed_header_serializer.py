# your_character_project/serializers/fixed_header_serializer.py

from io import BytesIO
from common_types import _pack_bytes # 引入 pack_bytes 函式

# 假設固定頭部是 30 位元組
FIXED_HEADER_LENGTH = 30

def serialize_fixed_header(header_data: dict, stream: BytesIO):
    """
    序列化固定頭部數據。此為空殼實作。
    Args:
        header_data: 包含固定頭部數據的字典。
        stream: BytesIO 串流物件，用於寫入位元組。
    """
    current_pos = stream.tell()
    print(f"    [偏移: {current_pos}] 開始序列化固定頭部 (空殼實作)。")

    # 實際實作時，你會使用 header_data 中的值來打包
    # stream.write(_pack_bytes(header_data.get('signature', b'CHAR')))
    # stream.write(_pack_uint8(header_data.get('major_version', 1)))
    # ...

    # 空殼實作：填充固定長度的 0x00
    stream.write(_pack_bytes(b'\x00' * FIXED_HEADER_LENGTH))

    print(f"    固定頭部序列化完成 (空殼實作)。下一個寫入位置: {stream.tell()}")