# ph-editor/compare/hair.py
from typing import Dict, Any

from utils.utils import get_nested_value, convert_rgba_to_hex_aa

HAIR_KEY_NAME_MAP = {
    # back_hair
    "bh_name": "🏷️後髮",
    # front_hair
    "fh_name": "🏷️前髮",
    # side_hair
    "sh_name": "🏷️側髮",
    # hair main color
    "h_color": "髮色",
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

    temp_results = {
        "h_color": convert_rgba_to_hex_aa(get_nested_value(d, "hair.back_hair.color", "")),
        "h_shine1": convert_rgba_to_hex_aa(get_nested_value(d, "hair.back_hair.shine1_color", "")),
        "h_effect1": get_nested_value(d, "hair.back_hair.shine1_effect", 0),
        "h_shine2": convert_rgba_to_hex_aa(get_nested_value(d, "hair.back_hair.shine2_color", "")),
        "h_effect2": get_nested_value(d, "hair.back_hair.shine2_effect", 0)
    }

    result["h_color"] = (
        f"{temp_results['h_color']} {temp_results['h_shine1']} {temp_results['h_effect1']} "
        f"{temp_results['h_shine2']} {temp_results['h_effect2']}"
    )
    
    return result
