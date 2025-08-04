# ph-editor/utils/utils.py
import re
from typing import Dict, Any, Optional


def get_nested_value(
    data: Dict[str, Any],
    keys: str,
    default_value: Optional[Any] = None
) -> Any:
    if isinstance(keys, str):
        key_list = keys.split('.')
    else:
        return default_value

    current_data = data
    for key in key_list:
        if isinstance(current_data, dict):
            current_data = current_data.get(key)
            if current_data is None:
                return default_value
        else:
            return default_value
    
    return current_data if current_data is not None else default_value


def convert_rgba_to_hex_aa(rgba_string: str) -> str:
    """
    將 (R, G, B, A) 字串格式的顏色轉換為 #RRGGBBAA 十六進位格式。

    Args:
        rgba_string: 輸入的顏色字串，例如 "(0, 90, 99, 255)"。

    Returns:
        #RRGGBBAA 格式的十六進位字串，如果輸入無效則返回空字串 ""。
    """
    if not isinstance(rgba_string, str):
        return ""

    # 使用正規表達式匹配並提取數字
    # \s* 匹配零個或多個空白字符
    # (\d+) 匹配一個或多個數字，並捕獲為一個組
    # ?: 可以讓它匹配 0~255，因為 int() 會處理
    match = re.match(r'^\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)$', rgba_string)

    if not match:
        return "" # 格式不符

    try:
        # 從匹配的組中提取並轉換為整數
        r = int(match.group(1))
        g = int(match.group(2))
        b = int(match.group(3))
        a = int(match.group(4))

        # 檢查 RGB 和 A 的值是否在有效範圍內
        if not (0 <= r <= 255 and \
                0 <= g <= 255 and \
                0 <= b <= 255 and \
                0 <= a <= 255): # A 這裡也是 0-255，符合你的輸入格式
            return "" # 值超出範圍

        # 將 RGB 值轉換為兩位十六進位
        hex_r = f"{r:02X}"
        hex_g = f"{g:02X}"
        hex_b = f"{b:02X}"

        # 將 Alpha 值轉換為兩位十六進位
        hex_a = f"{a:02X}"

        return f"#{hex_r}{hex_g}{hex_b}{hex_a}"

    except ValueError:
        return "" # 數字轉換錯誤 (理論上被 regex 擋掉，但多一層保護)
    except Exception:
        return "" # 捕捉所有其他潛在意外


def format_attributes_to_string(*args):
    formatted_parts = []
    for num in args:
        # 用 '_' 補足 3 格寬度、右對齊
        formatted_parts.append(f"{num:>3}".replace(" ", "."))
    
    return ".".join(formatted_parts)


def join_numbers_with_commas(*args):
    """
    將任意數量的數字用逗號分隔，轉為字串。

    範例：
    >>> join_numbers_with_commas(1, 20, 300)
    '1,20,300'
    """
    return " ".join(str(int(num)) for num in args)
    
    
def format_hsv_to_string(h, s, v):
    return f"({h},{s},{v})"
    
    
def format_hsva_to_string(h, s, v, a):
    return f"({h},{s},{v},{a})"