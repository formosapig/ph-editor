# your_character_project/serializers/face_serializer.py

from io import BytesIO
from common_types import _pack_bytes

# 假設臉部數據區塊固定是 120 位元組
FACE_DATA_LENGTH = 120

def serialize_face_data(face_data: dict, stream: BytesIO):
    """
    序列化臉部數據。此為空殼實作。
    Args:
        face_data: 包含臉部數據的字典。
        stream: BytesIO 串流物件，用於寫入位元組。
    """
    current_pos = stream.tell()
    print(f"    [偏移: {current_pos}] 開始序列化臉部數據 (空殼實作)。")

    # 空殼實作：填充固定長度的 0x00
    stream.write(_pack_bytes(b'\x00' * FACE_DATA_LENGTH))

    print(f"    臉部數據序列化完成 (空殼實作)。下一個寫入位置: {stream.tell()}")