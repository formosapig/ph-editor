# your_character_project/serializers/fixed_header_serializer.py

from io import BytesIO
from common_types import _pack_bytes, _pack_uint32  # 確保引入必要的打包函式

def serialize_fixed_header(header_data: dict, stream: BytesIO):
    """
    序列化固定頭部數據。
    
    Args:
        header_data: 包含固定頭部數據的字典，應包含 'mark', 'strange', 'version'。
        stream: BytesIO 串流物件，用於寫入位元組。
    """
    current_pos = stream.tell()
    print(f"    [偏移: {current_pos}] 開始序列化固定頭部。")

    # 處理 mark（15 bytes, ASCII）
    mark = header_data.get('mark', '')
    mark_bytes = mark.encode('ascii')
    mark_bytes = mark_bytes.ljust(15, b'\x00')[:15]
    stream.write(_pack_bytes(mark_bytes))

    # 處理 strange（4 bytes, UTF-8）
    strange = header_data.get('strange', '')
    strange_bytes = strange.encode('utf-8')
    strange_bytes = strange_bytes.ljust(4, b'\x00')[:4]
    stream.write(_pack_bytes(strange_bytes))

    # Padding（7 bytes）
    stream.write(_pack_bytes(b'\x00' * 7))

    # 版本號（4 bytes, uint32）
    version = header_data.get('version', 0)
    stream.write(_pack_uint32(version))

    print(f"    固定頭部序列化完成。下一個寫入位置: {stream.tell()}")
