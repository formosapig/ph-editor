# ph-editor/compare/clothing_compare.py
import math
from typing import Dict, Any
from utils.utils import (
    get_nested_value,
    convert_rgba_to_hex_aa,
    format_attributes_to_string,
    format_hsv_to_string,
    format_hsva_to_string,
)
from game_data.clothing_data import is_colorful, is_nashi


CLOTHING_KEY_NAME_MAP = {

    # clothing set...
    "c_set": "️種類",
    # 上衣 clothing.top.#name
    "c_top": "👗上衣",
    # 主色
    "c_top_main": "主色",
    # 副色
    "c_top_sub": "副色",
    
    # 下著 bottom
    "c_bottom": "👗下著",
    # 主色
    "c_bottom_main": "主色",
    # 副色
    "c_bottom_sub": "副色",
    
    # 胸罩 bra
    "c_bra": "👗胸罩",
    # 主色
    "c_bra_main": "主色",
    # 副色
    "c_bra_sub": "副色",
    
    # 內褲 panty
    "c_panty": "👗內褲",
    # 主色
    "c_panty_main": "主色",
    # 副色
    "c_panty_sub": "副色",
    
    # 泳衣 swimsuit
    "c_swimsuit": "👗泳衣",
    # 主色
    "c_swimsuit_main": "主色",
    # 副色
    "c_swimsuit_sub": "副色",
    
    # 泳衣-上衣 swimsuit_top
    "c_swimsuit_top": "👗泳衣-上衣",
    # 主色
    "c_swimsuit_top_main": "主色",
    # 副色
    "c_swimsuit_top_sub": "副色",
    
    # 泳衣-下著 swimsuit_bottom
    "c_swimsuit_bottom": "👗泳衣-下著",
    # 主色
    "c_swimsuit_bottom_main": "主色",
    # 副色
    "c_swimsuit_bottom_sub": "副色",
    
    # 手套 gloves
    "c_gloves": "👗手套",
    # 主色
    "c_gloves_main": "主色",
    # 副色
    "c_gloves_sub": "副色",
    
    # 褲襪 pantyhose
    "c_pantyhose": "👗️褲襪",
    # 主色
    "c_pantyhose_main": "主色",
    # 副色
    "c_pantyhose_sub": "副色",
    
    # 襪子 socks
    "c_socks": "👗️襪子",
    # 主色
    "c_socks_main": "主色",
    # 副色
    "c_socks_sub": "副色",
    
    # 鞋子 shoes
    "c_shoes": "👗鞋子",
    # 主色
    "c_shoes_main": "主色",
    # 副色
    "c_shoes_sub": "副色",
}


CLOTHING_KEY_BLOCK_MAP = {key: 'clothing' for key in CLOTHING_KEY_NAME_MAP}

    
def flatten_clothing_data(d: Dict[str, Any]) -> Dict[str, Any]:
    result = {}
    
    # 根據 clothing_set 決定要處理哪些項目
    clothing_type = get_nested_value(d, "clothing.clothing_set", "")
    result["c_set"] = clothing_type

    # 宣告所有可能的服裝項目
    all_array = ['top', 'bottom', 'bra', 'panty', 'swimsuit', 'swimsuit_top', 'swimsuit_bottom', 'gloves', 'pantyhose', 'socks', 'shoes']

    # 根據 clothing_type 篩選出要處理的項目列表
    if clothing_type == "通常":
        # 處理通常服裝
        items_to_process = ['top', 'bottom', 'bra', 'panty', 'gloves', 'pantyhose', 'socks', 'shoes']
    elif clothing_type == "水著":
        # 處理水著
        items_to_process = ['swimsuit', 'swimsuit_top', 'swimsuit_bottom', 'gloves', 'pantyhose', 'socks', 'shoes']
    else:
        # 處理其他情況，例如 clothing_set 為空或未知
        items_to_process = []

    # 遍歷所有可能的項目，並根據 clothing_type 進行處理
    for item in all_array:
        if item in items_to_process:
            # 1. 取得基本資訊
            result[f"c_{item}"] = get_nested_value(d, f"clothing.{item}.#name", "")
            
            # 2. 取得所有顏色和強度相關的值
            temp = {
                "main_color": convert_rgba_to_hex_aa(get_nested_value(d, f"clothing.{item}.main_color", "")),
                "main_shine": convert_rgba_to_hex_aa(get_nested_value(d, f"clothing.{item}.main_shine", "")),
                "main_strength": get_nested_value(d, f"clothing.{item}.main_strength", -1),
                "main_texture": get_nested_value(d, f"clothing.{item}.main_texture", -1),
                "sub_color": convert_rgba_to_hex_aa(get_nested_value(d, f"clothing.{item}.sub_color", "")),
                "sub_shine": convert_rgba_to_hex_aa(get_nested_value(d, f"clothing.{item}.sub_shine", "")),
                "sub_strength": get_nested_value(d, f"clothing.{item}.sub_strength", -1),
                "sub_texture": get_nested_value(d, f"clothing.{item}.sub_texture", -1)
            }

            # 3. 根據 color_type 動態組合字串
            item_id = get_nested_value(d, f"clothing.{item}.id", -1)
            color_type = is_colorful(item, item_id)

            color_main_parts = []
            color_sub_parts = []

            if is_nashi(item, item_id):
                result[f"c_{item}"] = ""
                # pass
            else:
                if color_type == 1:
                    color_main_parts = [
                        temp["main_color"],
                        temp["main_shine"],
                        temp["main_strength"],
                        temp["main_texture"]
                    ]
                elif color_type in [2, 3]:
                    color_main_parts = [
                        temp["main_color"],
                        temp["main_shine"],
                        temp["main_strength"],
                        temp["main_texture"]
                    ]
                    color_sub_parts = [
                        temp["sub_color"],
                        temp["sub_shine"],
                        temp["sub_strength"],
                        temp["sub_texture"]
                    ]

            # 4. 使用 join() 優化字串組合
            result[f"c_{item}_main"] = " ".join(map(str, color_main_parts))
            result[f"c_{item}_sub"] = " ".join(map(str, color_sub_parts))
        else:
            # 如果項目不在要處理的清單中，將所有相關資料設為空字串
            result[f"c_{item}"] = ""
            result[f"c_{item}_main"] = ""
            result[f"c_{item}_sub"] = ""

    return result
