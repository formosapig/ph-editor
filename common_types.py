# ph-editor/core/common_types.py
# 以後整理時, 再搬到 core 去.

import struct
from io import BytesIO

# --- Bytes 相關函式 ---

def _read_bytes(stream: BytesIO, length: int) -> bytes:
    data = stream.read(length)
    if len(data) < length:
        raise EOFError(f"資料流結束，無法讀取 {length} 位元組。已讀取 {len(data)} 位元組。")
    return data

def _pack_bytes(data: bytes) -> bytes:
    return data

def _read_bytes_as_hex(stream: BytesIO, length: int) -> str:
    data = _read_bytes(stream, length)
    return ' '.join(f'{b:02X}' for b in data)


def _pack_hex_to_bytes(hex_str: str, length: int) -> bytes:
    # 移除空格
    hex_str = hex_str.replace(' ', '')
    # 轉成 bytes
    data = bytes.fromhex(hex_str)
    # 補齊或截斷
    if len(data) < length:
        data += b'\x00' * (length - len(data))
    return data[:length]
    
# --- 無符號整數相關函式 ---

def _read_uint8(stream: BytesIO) -> int:
    return struct.unpack('<B', _read_bytes(stream, 1))[0]

def _pack_uint8(value: int) -> bytes:
    return struct.pack('<B', value)

def _read_uint16(stream: BytesIO) -> int:
    return struct.unpack('<H', _read_bytes(stream, 2))[0]

def _pack_uint16(value: int) -> bytes:
    return struct.pack('<H', value)

def _read_uint32(stream: BytesIO) -> int:
    return struct.unpack('<I', _read_bytes(stream, 4))[0]

def _pack_uint32(value: int) -> bytes:
    return struct.pack('<I', value)


# --- 有符號整數相關函式 ---

def _read_int32(stream: BytesIO) -> int:
    return struct.unpack('<i', _read_bytes(stream, 4))[0]

def _pack_int32(value: int) -> bytes:
    return struct.pack('<i', value)


# --- 浮點數相關函式 ---

def _read_float(stream: BytesIO) -> float | None:
    bytes_data = stream.read(4)
    if len(bytes_data) < 4:
        raise EOFError("Attempted to read 4 bytes for float but stream ended.")
    value = struct.unpack('<f', bytes_data)[0]
    if value != value:  # NaN check
        return None
    return value

def _pack_float(value: float) -> bytes:
    return struct.pack('<f', value)

def _read_double(stream: BytesIO) -> float:
    return struct.unpack('<d', _read_bytes(stream, 8))[0]

def _pack_double(value: float) -> bytes:
    return struct.pack('<d', value)


# --- 顏色相關函式 ---

def _read_color(stream: BytesIO) -> dict:
    return {
        'r': _read_float(stream),
        'g': _read_float(stream),
        'b': _read_float(stream),
        'a': _read_float(stream),
    }

def _format_color_for_json(color_data: dict) -> str:
    if any(c is None or c != c for c in (color_data['r'], color_data['g'], color_data['b'], color_data['a'])):
        return "NaN"
    r = max(0, min(255, round(color_data['r'] * 255)))
    g = max(0, min(255, round(color_data['g'] * 255)))
    b = max(0, min(255, round(color_data['b'] * 255)))
    a = max(0, min(255, round(color_data['a'] * 255)))
    return f"({r}, {g}, {b}, {a})"

def _pack_color(color_str: str) -> bytes:
    if color_str == "NaN":
        return b''.join([_pack_float(0.0)] * 4)
    try:
        parts = color_str.strip("()").split(",")
        rgba = [int(p.strip()) for p in parts]
        if len(rgba) != 4:
            raise ValueError("Color string must have 4 components.")
        return b''.join([_pack_float(c / 255.0) for c in rgba])
    except Exception as e:
        raise ValueError(f"Invalid color string format: '{color_str}'. Error: {e}")

# 組合函式, 讀取並格式化一步到位
def _read_and_format_color(stream: BytesIO) -> str:
    return _format_color_for_json(_read_color(stream))


# --- 數值設定相關函式 ---
# 預設是 0.0 - 1.0 <==> 0 - 100 部份值比較奇怪需注意, 色相的話是 -50 ~ 50 

def _format_float_to_value(source: float, scale: float = 100, min_val: int = 0, max_val: int = 100) -> int:
    """
    將浮點數轉換為指定範圍內的整數百分比值。

    Args:
        source: 輸入的浮點數。
        scale: 乘數，預設為100，表示將小數轉成百分比。
        min_val: 輸出最小值，預設0。
        max_val: 輸出最大值，預設100。

    Returns:
        整數百分比，限制在 [min_val, max_val] 範圍內。
    """
    value = round(source * scale)
    if value < min_val or value > max_val:
        print(f"[WARN] Source {source} resulted in {value}%, clamped to [{min_val}, {max_val}].")
    return max(min_val, min(max_val, value))

def _parse_value_to_float(value: int, scale: float = 100, min_val: int = 0, max_val: int = 100) -> float:
    """
    將整數百分比轉回浮點數，並檢查範圍。

    Args:
        value: 整數。
        scale: 除數，預設為100。
        min_val: 百分比最小值。
        max_val: 百分比最大值。

    Returns:
        浮點數，對應百分比的比例值。

    Raises:
        ValueError: 若百分比不在 [min_val, max_val] 範圍內，會印出警告但仍回傳值。
    """
    if value < min_val or value > max_val:
        print(f"[WARN] Value {value}% out of range [{min_val}, {max_val}].")
    return value / scale

# 組合函式, 方便一次處理完...
def _read_and_format_to_value(stream: BytesIO, scale: float = 100, min_val: int = 0, max_val: int = 100) -> int:
    source = _read_float(stream)
    return _format_float_to_value(source, scale, min_val, max_val    )

# 組合函式, 方便一次處理完....
def _parse_and_pack_float(value: int, scale: float = 100, min_val: int = 0, max_val: int = 100) -> bytes:
    """
    將整數值 (通常是百分比 0-100) 轉為浮點數，並打包為 float32 bytes。
    """
    clamped_value = max(min_val, min(max_val, value))  # 確保值在合法範圍內
    float_value = clamped_value / scale
    return _pack_float(float_value)