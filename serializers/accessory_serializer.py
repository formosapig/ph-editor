# your_character_project/serializers/accessory_serializer.py

from io import BytesIO
from common_types import _pack_bytes

# 假設配飾數據區塊固定是 60 位元組
ACCESSORY_DATA_LENGTH = 60

def serialize_accessory_data(accessory_data: dict, stream: BytesIO):
    """
    序列化配飾數據。此為空殼實作。
    Args:
        accessory_data: 包含配飾數據的字典。
        stream: BytesIO 串流物件，用於寫入位元組。
    """
    current_pos = stream.tell()
    print(f"    [偏移: {current_pos}] 開始序列化配飾數據 (空殼實作)。")

    # 空殼實作：填充固定長度的 0x00
    stream.write(_pack_bytes(b'\x00' * ACCESSORY_DATA_LENGTH))

    print(f"    配飾數據序列化完成 (空殼實作)。下一個寫入位置: {stream.tell()}")