# ph-editor/compare/hair_compare.py
import logging
from typing import Dict, Any, Optional
from game_data.hair_data import is_nashi
from utils.utils import get_nested_value, convert_rgba_to_hex_aa


logger = logging.getLogger(__name__)
#logger.disabled = True


HAIR_KEY_NAME_MAP = {
    # back_hair
    "bh_name": "👩️後髮",
    # front_hair
    "fh_name": "👩️前髮",
    # side_hair
    "sh_name": "👩️側髮",
    # hair main color
    "h_color": "髮色",
}


HAIR_KEY_BLOCK_MAP = {key: 'hair' for key in HAIR_KEY_NAME_MAP}


def _get_hair_id(hair_id: str) -> Optional[tuple[int, int]]:
    if not hair_id:  # 空字串或 None
        return None
    
    # 嘗試清理掉括號後分割
    try:
        id_array = hair_id.strip().strip("()").split(",")
        if len(id_array) != 2:
            return None
        x = int(id_array[0].strip())
        y = int(id_array[1].strip())
        return (x, y)
    except ValueError:
        # 轉 int 失敗
        return None
    except Exception:
        # 其他不可預期錯誤
        return None

        
def flatten_hair_data(d: Dict[str, Any]) -> Dict[str, Any]:
    result = {}
    
    # back_hair
    result["bh_name"] = get_nested_value(d, "hair.back_hair.#name", "")
    
    # front_hair
    hair_id = _get_hair_id(get_nested_value(d, "hair.front_hair.id", None))
    if is_nashi("front", hair_id):
        result["fh_name"] = ""
    else:
        result["fh_name"] = get_nested_value(d, "hair.front_hair.#name", "")
    
    # side_hair
    hair_id = _get_hair_id(get_nested_value(d, "hair.side_hair.id", None))
    if is_nashi("side", hair_id):
        result["sh_name"] = ""
    else:
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
