# ph-editor/compare/accessory_compare.py
import math
from typing import Dict, Any
from utils.utils import (
    get_nested_value,
    convert_rgba_to_hex_aa,
    format_attributes_to_string,
    format_hsv_to_string,
    format_hsva_to_string,
)


ACCESSORY_KEY_NAME_MAP = {

    "a_01": "🏷️01",
    "a_02": "02",
    "a_03": "03",
    "a_04": "04",
    "a_05": "05",
    "a_06": "06",
    "a_07": "07",
    "a_08": "08",
    "a_09": "09",
    "a_10": "10",
    
}


ACCESSORY_KEY_BLOCK_MAP = {key: 'accessory' for key in ACCESSORY_KEY_NAME_MAP}

    
def flatten_accessory_data(d: Dict[str, Any]) -> Dict[str, Any]:
    result = {}
    
    for i in range(1, 11):
        item_key = f"a_{i:02d}"
        accessory_key = f"accessory_{i:02d}"
        
        # 檢查 type, id, slot 是否存在或有效
        # 如果其中一個不存在，就將 result[item_key] 設為空字串
        if (get_nested_value(d, f"accessory.{accessory_key}.type", -1) == -1 or
            get_nested_value(d, f"accessory.{accessory_key}.id", -1) == -1 or
            get_nested_value(d, f"accessory.{accessory_key}.slot", -1) == -1):
            result[item_key] = ""
        else:
            # 預設賦值，使用 get_nested_value 取得 #info
            result[item_key] = get_nested_value(d, f"accessory.{accessory_key}.#info", "")
    
    return result
