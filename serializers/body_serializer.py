# your_character_project/serializers/body_serializer.py

from io import BytesIO
from common_types import _pack_bytes

# 假設身體數據區塊固定是 80 位元組
BODY_DATA_LENGTH = 80

def serialize_body_data(body_data: dict, stream: BytesIO):
    """
    序列化身體數據。此為空殼實作。
    Args:
        body_data: 包含身體數據的字典。
        stream: BytesIO 串流物件，用於寫入位元組。
    """
    current_pos = stream.tell()
    print(f"    [偏移: {current_pos}] 開始序列化身體數據 (空殼實作)。")

    # 空殼實作：填充固定長度的 0x00
    stream.write(_pack_bytes(b'\x00' * BODY_DATA_LENGTH))

    print(f"    身體數據序列化完成 (空殼實作)。下一個寫入位置: {stream.tell()}")