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


CLOTHING_KEY_NAME_MAP = {

    # 上衣 clothing.top.#name
    "c_top": "🏷️上衣",
    # 主色
    "c_top_main_col": "主色",
    "c_top_main_shi": "光澤",
    "c_top_main_set": "設定",
    # 副色
    "c_top_sub_col": "副色",
    "c_top_sub_shi": "光澤",
    "c_top_sub_set": "設定",
    
    # 下著 bottom
    "c_bot": "🏷️下著",
    # 主色
    "c_bot_main_col": "主色",
    "c_bot_main_shi": "光澤",
    "c_bot_main_set": "設定",
    # 副色
    "c_bot_sub_col": "副色",
    "c_bot_sub_shi": "光澤",
    "c_bot_sub_set": "設定",
    
    # 胸罩 bra
    "c_bra": "🏷️胸罩",
    # 主色
    "c_bra_main_col": "主色",
    "c_bra_main_shi": "光澤",
    "c_bra_main_set": "設定",
    # 副色
    "c_bra_sub_col": "副色",
    "c_bra_sub_shi": "光澤",
    "c_bra_sub_set": "設定",
    
    # 內褲 panty
    "c_pan": "🏷️內褲",
    # 主色
    "c_pan_main_col": "主色",
    "c_pan_main_shi": "光澤",
    "c_pan_main_set": "設定",
    # 副色
    "c_pan_sub_col": "副色",
    "c_pan_sub_shi": "光澤",
    "c_pan_sub_set": "設定",
    
    # 泳衣 swimsuit
    "c_swi": "🏷️泳衣",
    # 主色
    "c_swi_main_col": "主色",
    "c_swi_main_shi": "光澤",
    "c_swi_main_set": "設定",
    # 副色
    "c_swi_sub_col": "副色",
    "c_swi_sub_shi": "光澤",
    "c_swi_sub_set": "設定",
    
    # 泳衣-上衣 swimsuit_top
    "c_swt": "🏷️泳衣-上衣",
    # 主色
    "c_swt_main_col": "主色",
    "c_swt_main_shi": "光澤",
    "c_swt_main_set": "設定",
    # 副色
    "c_swt_sub_col": "副色",
    "c_swt_sub_shi": "光澤",
    "c_swt_sub_set": "設定",
    
    # 泳衣-下著 swimsuit_bottom
    "c_swb": "🏷️泳衣-下著",
    # 主色
    "c_swb_main_col": "主色",
    "c_swb_main_shi": "光澤",
    "c_swb_main_set": "設定",
    # 副色
    "c_swb_sub_col": "副色",
    "c_swb_sub_shi": "光澤",
    "c_swb_sub_set": "設定",
    
    # 手套 gloves
    "c_glo": "🏷️手套",
    # 主色
    "c_glo_main_col": "主色",
    "c_glo_main_shi": "光澤",
    "c_glo_main_set": "設定",
    # 副色
    "c_glo_sub_col": "副色",
    "c_glo_sub_shi": "光澤",
    "c_glo_sub_set": "設定",
    
    # 褲襪 pantyhose
    "c_pty": "🏷️褲襪",
    # 主色
    "c_pty_main_col": "主色",
    "c_pty_main_shi": "光澤",
    "c_pty_main_set": "設定",
    # 副色
    "c_pty_sub_col": "副色",
    "c_pty_sub_shi": "光澤",
    "c_pty_sub_set": "設定",
    
    # 襪子 socks
    "c_soc": "🏷️襪子",
    # 主色
    "c_soc_main_col": "主色",
    "c_soc_main_shi": "光澤",
    "c_soc_main_set": "設定",
    # 副色
    "c_soc_sub_col": "副色",
    "c_soc_sub_shi": "光澤",
    "c_soc_sub_set": "設定",
    
    # 鞋子 shoes
    "c_sho": "🏷️鞋子",
    # 主色
    "c_sho_main_col": "主色",
    "c_sho_main_shi": "光澤",
    "c_sho_main_set": "設定",
    # 副色
    "c_sho_sub_col": "副色",
    "c_sho_sub_shi": "光澤",
    "c_sho_sub_set": "設定",
    
}


CLOTHING_KEY_BLOCK_MAP = {key: 'clothing' for key in CLOTHING_KEY_NAME_MAP}

    
def flatten_clothing_data(d: Dict[str, Any]) -> Dict[str, Any]:
    result = {}
    
    # 上衣 clothing.top.#name
    result["c_top"] = get_nested_value(d, "clothing.top.#name", "")
    # 主色
    result["c_top_main_col"] = convert_rgba_to_hex_aa(
    get_nested_value(d, "clothing.top.main_color", "")
    )
    result["c_top_main_shi"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.top.main_shine", "")
    )
    result["c_top_main_set"] = format_attributes_to_string(
        get_nested_value(d, "clothing.top.main_strength", -1),
        get_nested_value(d, "clothing.top.main_texture", -1)
    )
    # 副色
    result["c_top_sub_col"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.top.sub_color", "")
    )
    result["c_top_sub_shi"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.top.sub_shine", "")
    )
    result["c_top_sub_set"] = format_attributes_to_string(
        get_nested_value(d, "clothing.top.sub_strength", -1),
        get_nested_value(d, "clothing.top.sub_texture", -1)
    )

    # 下著 clothing.bottom.#name
    result["c_bot"] = get_nested_value(d, "clothing.bottom.#name", "")
    # 主色
    result["c_bot_main_col"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.bottom.main_color", "")
    )
    result["c_bot_main_shi"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.bottom.main_shine", "")
    )
    result["c_bot_main_set"] = format_attributes_to_string(
        get_nested_value(d, "clothing.bottom.main_strength", -1),
        get_nested_value(d, "clothing.bottom.main_texture", -1)
    )
    # 副色
    result["c_bot_sub_col"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.bottom.sub_color", "")
    )
    result["c_bot_sub_shi"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.bottom.sub_shine", "")
    )
    result["c_bot_sub_set"] = format_attributes_to_string(
        get_nested_value(d, "clothing.bottom.sub_strength", -1),
        get_nested_value(d, "clothing.bottom.sub_texture", -1)
    )

    # 胸罩 clothing.bra.#name
    result["c_bra"] = get_nested_value(d, "clothing.bra.#name", "")
    # 主色
    result["c_bra_main_col"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.bra.main_color", "")
    )
    result["c_bra_main_shi"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.bra.main_shine", "")
    )
    result["c_bra_main_set"] = format_attributes_to_string(
        get_nested_value(d, "clothing.bra.main_strength", -1),
        get_nested_value(d, "clothing.bra.main_texture", -1)
    )
    # 副色
    result["c_bra_sub_col"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.bra.sub_color", "")
    )
    result["c_bra_sub_shi"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.bra.sub_shine", "")
    )
    result["c_bra_sub_set"] = format_attributes_to_string(
        get_nested_value(d, "clothing.bra.sub_strength", -1),
        get_nested_value(d, "clothing.bra.sub_texture", -1)
    )
   
    # 內褲 clothing.panty.#name
    result["c_pan"] = get_nested_value(d, "clothing.panty.#name", "")
    # 主色
    result["c_pan_main_col"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.panty.main_color", "")
    )
    result["c_pan_main_shi"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.panty.main_shine", "")
    )
    result["c_pan_main_set"] = format_attributes_to_string(
        get_nested_value(d, "clothing.panty.main_strength", -1),
        get_nested_value(d, "clothing.panty.main_texture", -1)
    )
    # 副色
    result["c_pan_sub_col"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.panty.sub_color", "")
    )
    result["c_pan_sub_shi"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.panty.sub_shine", "")
    )
    result["c_pan_sub_set"] = format_attributes_to_string(
        get_nested_value(d, "clothing.panty.sub_strength", -1),
        get_nested_value(d, "clothing.panty.sub_texture", -1)
    )

    # 泳衣 clothing.swimsuit.#name
    result["c_swi"] = get_nested_value(d, "clothing.swimsuit.#name", "")
    # 主色
    result["c_swi_main_col"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.swimsuit.main_color", "")
    )
    result["c_swi_main_shi"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.swimsuit.main_shine", "")
    )
    result["c_swi_main_set"] = format_attributes_to_string(
        get_nested_value(d, "clothing.swimsuit.main_strength", -1),
        get_nested_value(d, "clothing.swimsuit.main_texture", -1)
    )
    # 副色
    result["c_swi_sub_col"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.swimsuit.sub_color", "")
    )
    result["c_swi_sub_shi"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.swimsuit.sub_shine", "")
    )
    result["c_swi_sub_set"] = format_attributes_to_string(
        get_nested_value(d, "clothing.swimsuit.sub_strength", -1),
        get_nested_value(d, "clothing.swimsuit.sub_texture", -1)
    )

    # 泳衣-上衣 clothing.swimsuit_top.#name
    result["c_swt"] = get_nested_value(d, "clothing.swimsuit_top.#name", "")
    # 主色
    result["c_swt_main_col"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.swimsuit_top.main_color", "")
    )
    result["c_swt_main_shi"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.swimsuit_top.main_shine", "")
    )
    result["c_swt_main_set"] = format_attributes_to_string(
        get_nested_value(d, "clothing.swimsuit_top.main_strength", -1),
        get_nested_value(d, "clothing.swimsuit_top.main_texture", -1)
    )
    # 副色
    result["c_swt_sub_col"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.swimsuit_top.sub_color", "")
    )
    result["c_swt_sub_shi"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.swimsuit_top.sub_shine", "")
    )
    result["c_swt_sub_set"] = format_attributes_to_string(
        get_nested_value(d, "clothing.swimsuit_top.sub_strength", -1),
        get_nested_value(d, "clothing.swimsuit_top.sub_texture", -1)
    )

    # 泳衣-下著 clothing.swimsuit_bottom.#name
    result["c_swb"] = get_nested_value(d, "clothing.swimsuit_bottom.#name", "")
    # 主色
    result["c_swb_main_col"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.swimsuit_bottom.main_color", "")
    )
    result["c_swb_main_shi"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.swimsuit_bottom.main_shine", "")
    )
    result["c_swb_main_set"] = format_attributes_to_string(
        get_nested_value(d, "clothing.swimsuit_bottom.main_strength", -1),
        get_nested_value(d, "clothing.swimsuit_bottom.main_texture", -1)
    )
    # 副色
    result["c_swb_sub_col"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.swimsuit_bottom.sub_color", "")
    )
    result["c_swb_sub_shi"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.swimsuit_bottom.sub_shine", "")
    )
    result["c_swb_sub_set"] = format_attributes_to_string(
        get_nested_value(d, "clothing.swimsuit_bottom.sub_strength", -1),
        get_nested_value(d, "clothing.swimsuit_bottom.sub_texture", -1)
    )

    # 手套 clothing.gloves.#name
    result["c_glo"] = get_nested_value(d, "clothing.gloves.#name", "")
    # 主色
    result["c_glo_main_col"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.gloves.main_color", "")
    )
    result["c_glo_main_shi"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.gloves.main_shine", "")
    )
    result["c_glo_main_set"] = format_attributes_to_string(
        get_nested_value(d, "clothing.gloves.main_strength", -1),
        get_nested_value(d, "clothing.gloves.main_texture", -1)
    )
    # 副色
    result["c_glo_sub_col"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.gloves.sub_color", "")
    )
    result["c_glo_sub_shi"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.gloves.sub_shine", "")
    )
    result["c_glo_sub_set"] = format_attributes_to_string(
        get_nested_value(d, "clothing.gloves.sub_strength", -1),
        get_nested_value(d, "clothing.gloves.sub_texture", -1)
    )

    # 褲襪 clothing.pantyhose.#name
    result["c_pty"] = get_nested_value(d, "clothing.pantyhose.#name", "")
    # 主色
    result["c_pty_main_col"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.pantyhose.main_color", "")
    )
    result["c_pty_main_shi"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.pantyhose.main_shine", "")
    )
    result["c_pty_main_set"] = format_attributes_to_string(
        get_nested_value(d, "clothing.pantyhose.main_strength", -1),
        get_nested_value(d, "clothing.pantyhose.main_texture", -1)
    )
    # 副色
    result["c_pty_sub_col"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.pantyhose.sub_color", "")
    )
    result["c_pty_sub_shi"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.pantyhose.sub_shine", "")
    )
    result["c_pty_sub_set"] = format_attributes_to_string(
        get_nested_value(d, "clothing.pantyhose.sub_strength", -1),
        get_nested_value(d, "clothing.pantyhose.sub_texture", -1)
    )

    # 襪子 clothing.socks.#name
    result["c_soc"] = get_nested_value(d, "clothing.socks.#name", "")
    # 主色
    result["c_soc_main_col"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.socks.main_color", "")
    )
    result["c_soc_main_shi"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.socks.main_shine", "")
    )
    result["c_soc_main_set"] = format_attributes_to_string(
        get_nested_value(d, "clothing.socks.main_strength", -1),
        get_nested_value(d, "clothing.socks.main_texture", -1)
    )
    # 副色
    result["c_soc_sub_col"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.socks.sub_color", "")
    )
    result["c_soc_sub_shi"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.socks.sub_shine", "")
    )
    result["c_soc_sub_set"] = format_attributes_to_string(
        get_nested_value(d, "clothing.socks.sub_strength", -1),
        get_nested_value(d, "clothing.socks.sub_texture", -1)
    )

    # 鞋子 clothing.shoes.#name
    result["c_sho"] = get_nested_value(d, "clothing.shoes.#name", "")
    # 主色
    result["c_sho_main_col"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.shoes.main_color", "")
    )
    result["c_sho_main_shi"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.shoes.main_shine", "")
    )
    result["c_sho_main_set"] = format_attributes_to_string(
        get_nested_value(d, "clothing.shoes.main_strength", -1),
        get_nested_value(d, "clothing.shoes.main_texture", -1)
    )
    # 副色
    result["c_sho_sub_col"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.shoes.sub_color", "")
    )
    result["c_sho_sub_shi"] = convert_rgba_to_hex_aa(
        get_nested_value(d, "clothing.shoes.sub_shine", "")
    )
    result["c_sho_sub_set"] = format_attributes_to_string(
        get_nested_value(d, "clothing.shoes.sub_strength", -1),
        get_nested_value(d, "clothing.shoes.sub_texture", -1)
    )

    return result
