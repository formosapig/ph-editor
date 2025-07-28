# ph-editor/compare/face.py
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
    
    result["a_01"] = get_nested_value(d, "accessory.accessory_01.#info", "")
    result["a_02"] = get_nested_value(d, "accessory.accessory_02.#info", "")    
    result["a_03"] = get_nested_value(d, "accessory.accessory_03.#info", "")
    result["a_04"] = get_nested_value(d, "accessory.accessory_04.#info", "")
    result["a_05"] = get_nested_value(d, "accessory.accessory_05.#info", "")
    result["a_06"] = get_nested_value(d, "accessory.accessory_06.#info", "")
    result["a_07"] = get_nested_value(d, "accessory.accessory_07.#info", "")
    result["a_08"] = get_nested_value(d, "accessory.accessory_08.#info", "")
    result["a_09"] = get_nested_value(d, "accessory.accessory_09.#info", "")
    result["a_10"] = get_nested_value(d, "accessory.accessory_10.#info", "")
    
    return result
