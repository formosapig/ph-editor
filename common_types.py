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

def _read_bytes_as_hex(stream: BytesIO, length: int) -> str:
    """
    從 BytesIO 串流讀取指定長度的位元組，並回傳 JSON 可接受的十六進位字串（帶 "0x" 前綴）。

    Args:
        stream: BytesIO 串流物件。
        length: 要讀取的位元組長度。

    Returns:
        十六進位字串，格式例如 "AA BB CC DD"。
    """
    data = _read_bytes(stream, length)
    hex_str = ' '.join(f'{b:02X}' for b in data)
    return hex_str
    
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

def _read_float(stream: BytesIO) -> float | None: # 修改返回類型提示
    """
    從 BytesIO 串流中讀取一個 32 位元浮點數。
    如果讀取到的值是 NaN，則返回 None。
    """
    bytes_data = stream.read(4)
    if len(bytes_data) < 4:
        raise EOFError("Attempted to read 4 bytes for float but stream ended.")
    
    value = struct.unpack('<f', bytes_data)[0]
    
    # 檢查是否為 NaN
    if value != value: # NaN 的一個特性是它不等於自身
        return None
    # 你也可以檢查正負無限大，如果需要的話
    # if value == float('inf') or value == float('-inf'):
    #     return None
        
    return value

def _read_double(stream: BytesIO) -> float:
    """從 BytesIO 串流中讀取一個雙精度浮點數 (8 位元組)。"""
    return struct.unpack('<d', _read_bytes(stream, 8))[0]

# --- 新增的顏色讀取與格式化函式 ---

def _read_color(stream: BytesIO) -> dict:
    """
    從串流中讀取一個顏色數據，包含 RGBA 四個浮點數 (4 * 4 = 16 位元組)。
    R, G, B, A 的值範圍通常為 0.0 到 1.0。
    """
    color_data = {
        'r': _read_float(stream),
        'g': _read_float(stream),
        'b': _read_float(stream),
        'a': _read_float(stream)
    }
    return color_data

def format_color_for_json(color_data: dict) -> str:
    """
    將解析後的顏色數據（包含 R, G, B, A 鍵的字典，值為 float 0.0-1.0）
    轉換為 (R, G, B, A) 格式的字串，其中 R, G, B, A 為 0-255 的整數。
    如果任何顏色分量是 None 或 NaN，則整個顏色字串表示為 "NaN"。
    """
    # 檢查任何一個顏色分量是否為 None 或 NaN
    # NaN 的特性是它不等於自身 (x != x)
    if (color_data['r'] is None or color_data['r'] != color_data['r'] or
        color_data['g'] is None or color_data['g'] != color_data['g'] or
        color_data['b'] is None or color_data['b'] != color_data['b'] or
        color_data['a'] is None or color_data['a'] != color_data['a']):
        return "NaN" # 如果任何分量是 None 或 NaN，則返回 "NaN" 字串

    # 進行轉換，確保值在 0-255 範圍內
    r_255 = max(0, min(255, round(color_data['r'] * 255)))
    g_255 = max(0, min(255, round(color_data['g'] * 255)))
    b_255 = max(0, min(255, round(color_data['b'] * 255)))
    a_255 = max(0, min(255, round(color_data['a'] * 255))) 

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