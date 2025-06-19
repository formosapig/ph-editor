# your_character_project/serializers/misc_serializer.py

from io import BytesIO
from common_types import _pack_bytes

# 假設其他零碎數據總共填充 50 位元組
MISC_DATA_LENGTH = 0

def serialize_misc_data(misc_data: dict, stream: BytesIO):
    """
    序列化其他零碎數據或填充無意義數據。此為空殼實作。
    Args:
        misc_data: 包含其他零碎數據的字典。
        stream: BytesIO 串流物件，用於寫入位元組。
    """
    current_pos = stream.tell()
    print(f"    [偏移: {current_pos}] 開始序列化其他零碎數據/填充無意義數據 (空殼實作)。")

    # 空殼實作：填充固定長度的 0x00
    stream.write(_pack_bytes(b'\x00' * MISC_DATA_LENGTH))

    print(f"    其他零碎數據序列化完成 (空殼實作)。下一個寫入位置: {stream.tell()}")