# ph-editor/compare/hair.py
from typing import Dict, Any

from utils.utils import get_nested_value, convert_rgba_to_hex_aa

HAIR_KEY_NAME_MAP = {
    
    # 共同資料段...
    # back_hair
    "bh_name": "後髮",
    # front_hair
    "fh_name": "前髮",
    # side_hair
    "sh_name": "側髮",
    # hair main color
    "h_color": "髮色",
    # hair shine color 1
    "h_shine1": "光澤1",
    # back_hair.shine1_effect
    "h_effect1": "絞",
    # hair shine color 2
    "h_shine2": "光澤2",
    # back_hari.shine2_effect
    "h_effect2": "絞",
}

HAIR_KEY_BLOCK_MAP = {key: 'hair' for key in HAIR_KEY_NAME_MAP}
    
def flatten_hair_data(d: Dict[str, Any]) -> Dict[str, Any]:
    result = {}
    
    # back_hair
    result["bh_name"] = get_nested_value(d, "hair.back_hair.#name", "")
    
    # front_hair
    result["fh_name"] = get_nested_value(d, "hair.front_hair.#name", "")
    
    # side_hair
    result["sh_name"] = get_nested_value(d, "hair.side_hair.#name", "")

    # hair main color
    result["h_color"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "hair.back_hair.color", "")
    )

    # hair shine color 1
    result["h_shine1"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "hair.back_hair.shine1_color", "")
    )

    # back_hair.shine1_effect
    result["h_effect1"] = get_nested_value(d, "hair.back_hair.shine1_effect", 0)

    # hair shine color 2
    result["h_shine2"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "hair.back_hair.shine2_color", "")
    )

    # back_hari.shine2_effect
    result["h_effect2"] = get_nested_value(d, "hair.back_hair.shine2_effect", 0)

    return result
