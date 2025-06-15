# your_character_project/core/common_types.py

import struct
from io import BytesIO

# --- 讀取 (Parsing) 相關函式 ---

def _read_bytes(stream: BytesIO, length: int) -> bytes:
    """
    從 BytesIO 串流中讀取指定長度的位元組。
    如果串流中的位元組不足，會拋出 EOFError。

    Args:
        stream: BytesIO 串流物件。
        length: 要讀取的位元組長度。

    Returns:
        讀取到的位元組資料。

    Raises:
        EOFError: 如果串流結束且無法讀取足夠的位元組。
    """
    data = stream.read(length)
    if len(data) < length:
        raise EOFError(f"資料流結束，無法讀取 {length} 位元組。已讀取 {len(data)} 位元組。")
    return data

def _read_uint8(stream: BytesIO) -> int:
    """從 BytesIO 串流中讀取一個無符號 8 位元整數 (1 位元組)。"""
    return struct.unpack('<B', _read_bytes(stream, 1))[0]

def _read_uint16(stream: BytesIO) -> int:
    """從 BytesIO 串流中讀取一個無符號 16 位元整數 (2 位元組)。"""
    return struct.unpack('<H', _read_bytes(stream, 2))[0]

def _read_uint32(stream: BytesIO) -> int:
    """從 BytesIO 串流中讀取一個無符號 32 位元整數 (4 位元組)。"""
    return struct.unpack('<I', _read_bytes(stream, 4))[0]

def _read_int32(stream: BytesIO) -> int:
    """從 BytesIO 串流中讀取一個有符號 32 位元整數 (4 位元組)。"""
    return struct.unpack('<i', _read_bytes(stream, 4))[0]

def _read_float(stream: BytesIO) -> float:
    """從 BytesIO 串流中讀取一個單精度浮點數 (4 位元組)。"""
    return struct.unpack('<f', _read_bytes(stream, 4))[0]

def _read_double(stream: BytesIO) -> float:
    """從 BytesIO 串流中讀取一個雙精度浮點數 (8 位元組)。"""
    return struct.unpack('<d', _read_bytes(stream, 8))[0]

# --- 新增的顏色讀取函式 ---
def _read_color(stream: BytesIO) -> dict:
    """
    從串流中讀取一個顏色數據，包含 RGBA 四個浮點數 (4 * 4 = 16 位元組)。

    Returns:
        一個字典，格式為 {'r': float, 'g': float, 'b': float, 'a': float}。
    """
    color_data = {
        'r': _read_float(stream),
        'g': _read_float(stream),
        'b': _read_float(stream),
        'a': _read_float(stream)
    }
    return color_data

def _format_color_for_json(color_data: dict) -> str:
    """
    將顏色字典轉換為 (R, G, B, A) 字串格式，其中 R, G, B, A 範圍為 0-255。
    """
    if not isinstance(color_data, dict) or \
       'r' not in color_data or 'g' not in color_data or \
       'b' not in color_data or 'a' not in color_data:
        return str(color_data) # 返回原始數據的字串表示，以防格式不正確

    # 將 0.0-1.0 的浮點數轉換為 0-255 的整數
    r_255 = round(color_data['r'] * 255)
    g_255 = round(color_data['g'] * 255)
    b_255 = round(color_data['b'] * 255)
    # Alpha 值通常也顯示為 0-255，或者保持 0.0-1.0 根據實際需求，
    # 如果你也希望 alpha 顯示為 0-255，則也乘 255
    a_255 = round(color_data['a'] * 255) 

    # 返回 (R, G, B, A) 格式的字串
    return f"({r_255}, {g_255}, {b_255}, {a_255})"


# --- 寫入 (Serialization) 相關函式 ---

def _pack_bytes(data: bytes) -> bytes:
    """
    直接回傳位元組資料 (用於寫入)。
    Args:
        data: 要寫入的位元組資料。
    Returns:
        位元組資料。
    """
    return data

def _pack_uint8(value: int) -> bytes:
    """將一個整數打包成無符號 8 位元整數 (1 位元組)。"""
    return struct.pack('<B', value)

def _pack_uint16(value: int) -> bytes:
    """將一個整數打包成無符號 16 位元整數 (2 位元組)。"""
    return struct.pack('<H', value)

def _pack_uint32(value: int) -> bytes:
    """將一個整數打包成無符號 32 位元整數 (4 位元組)。"""
    return struct.pack('<I', value)

def _pack_int32(value: int) -> bytes:
    """將一個整數打包成有符號 32 位元整數 (4 位元組)。"""
    return struct.pack('<i', value)

def _pack_float(value: float) -> bytes:
    """將一個浮點數打包成單精度浮點數 (4 位元組)。"""
    return struct.pack('<f', value)

def _pack_double(value: float) -> bytes:
    """將一個浮點數打包成雙精度浮點數 (8 位元組)。"""
    return struct.pack('<d', value)