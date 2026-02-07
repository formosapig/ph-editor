# ph-editor/compare/body_compare.py
import math
from typing import Dict, Any, Optional
from utils.utils import (
    get_nested_value,
    convert_rgba_to_hex_aa,
    format_attributes_to_string,
    format_hsv_to_string,
    format_hsva_to_string,
)
from game_data.body_data import is_nashi
from game_data.cup_data import get_sister_cup_value

def calculate_value_by_height(height: int) -> Optional[int]:
    base_value = 50
    min_height = 140
    max_height = 177
    range_start_value = 50
    range_end_value = 100

    height_range_diff = max_height - min_height

    if height_range_diff == 0:
        return int(base_value) if height >= min_height else None

    raw_result = base_value + ((height - min_height) / height_range_diff) * (range_end_value - range_start_value)

    rounded_result = round(raw_result)

    if 0 <= rounded_result <= 100:
        return int(rounded_result)
    else:
        return None


BODY_KEY_NAME_MAP = {
    
    # 身高設定 story.profile.height
    "b_pro_hei": "身高設定",
    # 全部 (body.overall.height, body.overall.head_size)
    "b_overall": "👍全体(頭圍)",
    # body.overall.#skin_name
    "b_ove_skin": "肌膚肉感",
    # body.overall.hue/body.overall.saturation/body.overall.valu
    "b_ove_hsv": "色相光澤",
    
    # 胸部設定 story.profile.cup
    "b_pro_cup": "胸圍設定",
    # 全部 body.breast.size ...
    "b_bre_all": "👍全体",
    # 乳頭 body.breast.nipples.#name
    "b_bre_nip": "乳頭乳暈",
    # 色相 body.breast.nipples.hue, saturation, value, alpha
    "b_bre_nip_hsva": "色相光澤",
    
    # 上半身
    "b_upp": "👍上半身",
    
    # 下半身
    "b_low": "👍下半身",
    
    # 腕
    "b_arm": "👍腕",
    
    # 腳
    "b_leg": "👍腳",
    
    # 指甲 hsva
    "b_nai_hsva": "👍指甲色",
    # 指甲油
    "b_nai_pol": "指甲油",
    
    # 陰毛
    "b_pub": "👍陰毛",
    
    # 曬痕
    "b_tan": "👍曬痕",
    
    # 刺青
    "b_tat": "👍刺青",
}


BODY_KEY_BLOCK_MAP = {key: 'body' for key in BODY_KEY_NAME_MAP}

    
def flatten_body_data(d: Dict[str, Any]) -> Dict[str, Any]:
    result = {}
    
    # 身高設定 story.profile.height
    val_origin_height = get_nested_value(d, "story.profile.height", -1)
    val_setting_height = calculate_value_by_height(val_origin_height)
    val_game_height = get_nested_value(d, "body.overall.height", -1)
    # 如果 val_setting_height 不是 None，就格式化顯示；否則給空字串
    result["b_pro_hei"] = (
        f"{'❌️' if val_setting_height != val_game_height else ''}"
        f" {val_origin_height} cm {val_setting_height} → {val_game_height}"
        if val_setting_height is not None else f"{val_game_height}"
    )
    # 全部 (body.overall.height, body.overall.head_size)
    result["b_overall"] = get_nested_value(d, "body.overall.head_size", -1)
    # body.overall.#skin_name
    result["b_ove_skin"] = (
        f"{get_nested_value(d, 'body.overall.#skin_name', '')}: "
        f"{get_nested_value(d, 'body.overall.flesh_strength', -1)}"
    )
    # body.overall.hue/body.overall.saturation/body.overall.value...
    overall_hsv = format_hsv_to_string(
        get_nested_value(d, "body.overall.hue", -1),
        get_nested_value(d, "body.overall.saturation", -1),
        get_nested_value(d, "body.overall.value", -1)
    )
    result["b_ove_hsv"] = (
        f"{overall_hsv} "
        f"({get_nested_value(d, 'body.overall.gloss_strength', -1)},"
        f"{get_nested_value(d, 'body.overall.gloss_texture', -1)})"
    )

    # 胸部設定 story.profile.cup
    val_origin_cup = get_nested_value(d, "story.profile.cup", "")
    val_setting_cup = get_sister_cup_value(val_origin_cup)
    val_game_cup = get_nested_value(d, "body.breast.size", -1)
    
    result["b_pro_cup"] = (
        f"{'❌ ' + str(val_game_cup) + ' → ' if val_setting_cup != val_game_cup else ''}"
        f"✔️ {val_setting_cup} ({val_origin_cup})"
        if val_setting_cup is not None else
        f"{val_game_cup}"
    )
    
    # 全部 body.breast.size ...
    result["b_bre_all"] = format_attributes_to_string(
        #get_nested_value(d, "body.breast.size", -1),
        get_nested_value(d, "body.breast.vertical_position", -1),
        get_nested_value(d, "body.breast.horizontal_spread", -1),
        get_nested_value(d, "body.breast.horizontal_position", -1),
        get_nested_value(d, "body.breast.angle", -1),
        get_nested_value(d, "body.breast.firmness", -1),
        get_nested_value(d, "body.breast.areola_prominence", -1),
        get_nested_value(d, "body.breast.nipple_thickness", -1),
        get_nested_value(d, "body.breast.nipple_erectness", -1),
        get_nested_value(d, "body.breast.softness", -1),
        get_nested_value(d, "body.breast.weight", -1)
    )
    # 乳頭 body.breast.nipples.#name
    result["b_bre_nip"] = (
        f"{get_nested_value(d, 'body.breast.nipples.#name', '')}: "
        f"{get_nested_value(d, 'body.breast.nipples.areola_size', -1)}"
    )
    # 色相 body.breast.nipples.hue, saturation, value, alpha
    nipples_hsva = format_hsva_to_string(
        get_nested_value(d, "body.breast.nipples.hue", -1),
        get_nested_value(d, "body.breast.nipples.saturation", -1),
        get_nested_value(d, "body.breast.nipples.value", -1),
        get_nested_value(d, "body.breast.nipples.alpha", -1)
    )
    result["b_bre_nip_hsva"] = (
        f"{nipples_hsva} "
        f"({get_nested_value(d, 'body.breast.nipples.gloss_strength', -1)},"
        f"{get_nested_value(d, 'body.breast.nipples.gloss_texture', -1)})"
    )
    
    # 上半身
    result["b_upp"] = format_attributes_to_string(
        get_nested_value(d, "body.upper_body.neck_width", -1),
        get_nested_value(d, "body.upper_body.neck_thickness", -1),
        get_nested_value(d, "body.upper_body.torso_shoulder_width", -1),
        get_nested_value(d, "body.upper_body.torso_shoulder_thickness", -1),
        get_nested_value(d, "body.upper_body.torso_upper_width", -1),
        get_nested_value(d, "body.upper_body.torso_upper_thickness", -1),
        get_nested_value(d, "body.upper_body.torso_lower_width", -1),
        get_nested_value(d, "body.upper_body.torso_lower_thickness", -1)
    )

    # 下半身
    result["b_low"] = format_attributes_to_string(
        get_nested_value(d, "body.lower_body.waist_position", -1),
        get_nested_value(d, "body.lower_body.waist_upper_width", -1),
        get_nested_value(d, "body.lower_body.waist_upper_thickness", -1),
        get_nested_value(d, "body.lower_body.waist_lower_width", -1),
        get_nested_value(d, "body.lower_body.waist_lower_thickness", -1),
        get_nested_value(d, "body.lower_body.hip_size", -1),
        get_nested_value(d, "body.lower_body.hip_angle", -1)
    )
    
    # 腕
    result["b_arm"] = format_attributes_to_string(
        get_nested_value(d, "body.arms.shoulder", -1),
        get_nested_value(d, "body.arms.upper_arm", -1),
        get_nested_value(d, "body.arms.forearm", -1)
    )

    # 腳
    result["b_leg"] = format_attributes_to_string(
        get_nested_value(d, "body.legs.thigh_upper", -1),
        get_nested_value(d, "body.legs.thigh_lower", -1),
        get_nested_value(d, "body.legs.calf", -1),
        get_nested_value(d, "body.legs.ankle", -1)
    )

    # 指甲 hsva
    nails_hsva = format_hsva_to_string(
        get_nested_value(d, "body.nails.hue", -1),
        get_nested_value(d, "body.nails.saturation", -1),
        get_nested_value(d, "body.nails.value", -1),
        get_nested_value(d, "body.nails.alpha", -1)
    )
    result["b_nai_hsva"] = (
        f"{nails_hsva} "
        f"({get_nested_value(d, 'body.nails.gloss_strength', -1)},"
        f"{get_nested_value(d, 'body.nails.gloss_texture', -1)})"
    )
    # 指甲油, Color Code 夾資料時, 只能用空白隔開資料
    result["b_nai_pol"] = (
        f"{convert_rgba_to_hex_aa(get_nested_value(d, 'body.nails.polish.color', -1))} "
        f"{get_nested_value(d, "body.nails.polish.shine_strength", -1)} "
        f"{get_nested_value(d, "body.nails.polish.shine_texture", -1)}"
    )
    
    # 陰毛
    result["b_pub"] = (
        f"{get_nested_value(d, 'body.pubic_hair.#name', '')} "
        f"{convert_rgba_to_hex_aa(get_nested_value(d, 'body.pubic_hair.color', -1))}"
        if not is_nashi('pubic_hair', get_nested_value(d, 'body.pubic_hair.id', -1)) else ""
    )

    # 曬痕
    if is_nashi('tan_lines', get_nested_value(d, "body.tan_lines.id", -1)):
        result["b_tan"] = ""
    else:    
        tan_lines_hsva = format_hsva_to_string(
            get_nested_value(d, "body.tan_lines.hue", -1),
            get_nested_value(d, "body.tan_lines.saturation", -1),
            get_nested_value(d, "body.tan_lines.value", -1),
            get_nested_value(d, "body.tan_lines.intensity", -1)
        )
        result["b_tan"] = (
            f"{get_nested_value(d, 'body.tan_lines.#name', '')} "
            f"{tan_lines_hsva}"
        )    

    # 刺青
    result["b_tat"] = (
        f"{get_nested_value(d, 'body.tattoo.#name', '')} "
        f"{convert_rgba_to_hex_aa(get_nested_value(d, 'body.tattoo.color', -1))}"
        if not is_nashi('tattoo', get_nested_value(d, 'body.tattoo.id', -1)) else ""
    )

    return result
