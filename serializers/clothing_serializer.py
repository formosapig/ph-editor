# your_character_project/serializers/clothing_serializer.py

from io import BytesIO
from common_types import _pack_bytes

# 假設衣服數據區塊固定是 150 位元組
CLOTHING_DATA_LENGTH = 150

def serialize_clothing_data(clothing_data: dict, stream: BytesIO):
    """
    序列化衣服數據。此為空殼實作。
    Args:
        clothing_data: 包含衣服數據的字典。
        stream: BytesIO 串流物件，用於寫入位元組。
    """
    current_pos = stream.tell()
    print(f"    [偏移: {current_pos}] 開始序列化衣服數據 (空殼實作)。")

    # 空殼實作：填充固定長度的 0x00
    stream.write(_pack_bytes(b'\x00' * CLOTHING_DATA_LENGTH))

    print(f"    衣服數據序列化完成 (空殼實作)。下一個寫入位置: {stream.tell()}")