# ph-editor/compare/face_compare.py
from typing import Dict, Any

from game_data.face_data import is_nashi
from utils.utils import (
    get_nested_value,
    convert_rgba_to_hex_aa,
    format_attributes_to_string,
    join_numbers_with_commas,
)


FACE_KEY_NAME_MAP = {
    
    # 全體 (overall.over_width, upper_parth_depth, upper_part.height, lower_part_depth, lower_part_width)
    "f_overall": "😀️全體",
    # 輪廓 contour
    "f_contour": "輪廓",
    # 肌肉 muscle
    "f_muscle": "肌肉",
    # 皺紋 wrinkle
    "f_wrinkle": "皺紋",
    
    # 耳朵 (ears.size, ears.angle_y, ears.angle_z, ears.upper_shape, ears.lower_shape)
    "f_ears": "😀️耳朵",
    
    # 眉毛 (eyebrows.height, eyebrows.horizontal_position, eyebrows.angle_z, eyebrows.inner_shaper, eyebrows.outer_shape
    "f_eye_all": "😀️眉毛",
    # 眉形 eyebrows.name
    "f_eyebrows": "眉形顏色效果",
    
    # 睫毛 eyelashes.#name
    "f_eyelashes": "😀️睫毛顏色效果",
    
    # 眼睛 eyes.height, eyes.horizontal_position, eyes ... all
    "f_eyes": "😀️眼睛",
        
    # 眼球 (左,右統一喔!!) (eyeballs.pupil_v ... 
    "f_eyeba_all": "😀️眼球",
    # 眼球 eyeballs.left_eyeball.#name
    "f_eyeba_type": "種類鞏膜瞳孔設定",
    # 眼神 eyeballs.#name
    "f_eyeba_hig": "眼神顏色",
    
    # 鼻子
    "f_nose": "😀️鼻子",
    
    # 臉頰
    "f_cheeks": "😀️臉頰",
   
    # 嘴唇
    "f_mouth": "😀️嘴唇",

    # 下巴
    "f_chin": "😀️下巴",
    
    # 痣
    "f_mole": "😀️痣",
    
    # 化妝 眼影
    "f_mak_eye": "😀️眼影",

    # 腮紅
    "f_mak_blu": "😀️腮紅",

    # 唇膏
    "f_mak_lip": "😀️唇膏",
    
    # 刺青
    "f_tattoo": "😀️刺青",
}

FACE_KEY_BLOCK_MAP = {key: 'face' for key in FACE_KEY_NAME_MAP}
    
def flatten_face_data(d: Dict[str, Any]) -> Dict[str, Any]:
    result = {}
    
    # 全體 (overall.over_width, upper_parth_depth, upper_part.height, lower_part_depth, lower_part_width)
    result["f_overall"] = join_numbers_with_commas(
        get_nested_value(d, "face.overall.overall_width", -1),
        get_nested_value(d, "face.overall.upper_part_depth", -1),
        get_nested_value(d, "face.overall.upper_part_height", -1),
        get_nested_value(d, "face.overall.lower_part_depth", -1),
        get_nested_value(d, "face.overall.lower_part_width", -1),
    )
    # 輪廓 contour
    result["f_contour"] = get_nested_value(d, "face.overall.#contour_name", "")
    # 肌肉 muscle
    result["f_muscle"] = get_nested_value(d, "face.overall.#muscle_name", "")
    # 皺紋 wrinkle
    result["f_wrinkle"] = (
        f"{get_nested_value(d, 'face.overall.#wrinkle_name', '')} "
        f"{get_nested_value(d, 'face.overall.wrinkle_depth', -1)}"
        if not is_nashi('wrinkle', get_nested_value(d, 'face.overall.wrinkle_id', -1))
        else ""
    )  

    # 耳朵 (ears.size, ears.angle_y, ears.angle_x, ears.upper_shape, ears.lower_shape)
    result["f_ears"] = format_attributes_to_string(
        get_nested_value(d, "face.ears.size", -1),
        get_nested_value(d, "face.ears.angle_y", -1),
        get_nested_value(d, "face.ears.angle_z", -1),
        get_nested_value(d, "face.ears.upper_shape", -1),
        get_nested_value(d, "face.ears.lower_shape", -1)
    )

    # 眉毛 (eyebrows.height, eyebrows.horizontal_position, eyebrows.angle_z, eyebrows.inner_shaper, eyebrows.outer_shape
    result["f_eye_all"] = format_attributes_to_string(
        get_nested_value(d, "face.eyebrows.height", -1),
        get_nested_value(d, "face.eyebrows.horizontal_position", -1),
        get_nested_value(d, "face.eyebrows.angle_z", -1),
        get_nested_value(d, "face.eyebrows.inner_shape", -1),
        get_nested_value(d, "face.eyebrows.outer_shape", -1)
    )
    # 眉形 eyebrows.#name
    result["f_eyebrows"] = (
        f"{get_nested_value(d, 'face.eyebrows.#name', '')} "
        f"{convert_rgba_to_hex_aa(get_nested_value(d, 'face.eyebrows.color', ''))} "
        f"{get_nested_value(d, 'face.eyebrows.strength', -1)} "
        f"{get_nested_value(d, 'face.eyebrows.texture', -1)}"
    )
    
    # 睫毛 eyelashes.#name
    result["f_eyelashes"] = (
        f"{get_nested_value(d, 'face.eyelashes.#name', '')} "
        f"{convert_rgba_to_hex_aa(get_nested_value(d, 'face.eyelashes.color', ''))} "
        f"{get_nested_value(d, 'face.eyelashes.strength', -1)} "
        f"{get_nested_value(d, 'face.eyelashes.texture', -1)}"
    )
    
    # 眼睛 eyes.height, eyes.horizontal_position, eyes ... all
    result["f_eyes"] = format_attributes_to_string(
        get_nested_value(d, "face.eyes.height", -1),
        get_nested_value(d, "face.eyes.horizontal_position", -1),
        get_nested_value(d, "face.eyes.depth", -1),
        get_nested_value(d, "face.eyes.width", -1),
        get_nested_value(d, "face.eyes.vertical_width", -1),
        get_nested_value(d, "face.eyes.angle_z", -1),
        get_nested_value(d, "face.eyes.angle_y", -1),
        get_nested_value(d, "face.eyes.inner_corner_h_pos", -1),
        get_nested_value(d, "face.eyes.outer_corner_h_pos", -1),
        get_nested_value(d, "face.eyes.inner_corner_v_pos", -1),
        get_nested_value(d, "face.eyes.outer_corner_v_pos", -1),
        get_nested_value(d, "face.eyes.eyelid_shape_1", -1),
        get_nested_value(d, "face.eyes.eyelid_shape_2", -1)
    )
    
    # 眼球 (左,右統一喔!!) (eyeballs.pupil_v ... 
    result["f_eyeba_all"] = format_attributes_to_string(
        get_nested_value(d, "face.eyeballs.pupil_v_adjustment", -1),
        get_nested_value(d, "face.eyeballs.pupil_width", -1),
        get_nested_value(d, "face.eyeballs.pupil_vertical_width", -1)
    )
    
    # 眼球 eyeballs.left_eyeball.#name
    result["f_eyeba_type"] = (
        f"{get_nested_value(d, 'face.eyeballs.left_eyeball.#name', '')} "
        f"{convert_rgba_to_hex_aa(get_nested_value(d, 'face.eyeballs.left_eyeball.sclera_color', ''))} "
        f"{convert_rgba_to_hex_aa(get_nested_value(d, 'face.eyeballs.left_eyeball.pupil_color', ''))} "
        f"{get_nested_value(d, 'face.eyeballs.left_eyeball.pupil_size', -1)} "
        f"{get_nested_value(d, 'face.eyeballs.left_eyeball.pupil_brightness', -1)}"
    )
    
    # 眼神 eyeballs.#name
    result["f_eyeba_hig"] = (
        f"{get_nested_value(d, 'face.eyeballs.#name', '')} "
        f"{convert_rgba_to_hex_aa(get_nested_value(d, 'face.eyeballs.highlight_color', ''))}"
    )

    # 鼻子
    result["f_nose"] = format_attributes_to_string(
        get_nested_value(d, "face.nose.overall_height", -1),
        get_nested_value(d, "face.nose.overall_depth", -1),
        get_nested_value(d, "face.nose.overall_angle_x", -1),
        get_nested_value(d, "face.nose.overall_width", -1),
        get_nested_value(d, "face.nose.bridge_height", -1),
        get_nested_value(d, "face.nose.bridge_width", -1),
        get_nested_value(d, "face.nose.bridge_shape", -1),
        get_nested_value(d, "face.nose.nostril_width", -1),
        get_nested_value(d, "face.nose.nostril_height", -1),
        get_nested_value(d, "face.nose.nostril_depth", -1),
        get_nested_value(d, "face.nose.nostril_angle_x", -1),
        get_nested_value(d, "face.nose.nostril_angle_z", -1),
        get_nested_value(d, "face.nose.tip_height", -1),
        get_nested_value(d, "face.nose.tip_angle_x", -1),
        get_nested_value(d, "face.nose.tip_size", -1)
    )
    
    # 臉頰
    result["f_cheeks"] = format_attributes_to_string(
        get_nested_value(d, "face.cheeks.lower_height", -1),
        get_nested_value(d, "face.cheeks.lower_depth", -1),
        get_nested_value(d, "face.cheeks.lower_width", -1),
        get_nested_value(d, "face.cheeks.upper_height", -1),
        get_nested_value(d, "face.cheeks.upper_depth", -1),
        get_nested_value(d, "face.cheeks.upper_width", -1)
    )

    # 嘴唇
    result["f_mouth"] = format_attributes_to_string(
        get_nested_value(d, "face.mouth.height", -1),
        get_nested_value(d, "face.mouth.width", -1),
        get_nested_value(d, "face.mouth.vertical_width", -1),
        get_nested_value(d, "face.mouth.depth", -1),
        get_nested_value(d, "face.mouth.upper_lip_shape", -1),
        get_nested_value(d, "face.mouth.lower_lip_shape", -1),
        get_nested_value(d, "face.mouth.corner_shape", -1)
    )

    # 下巴
    result["f_chin"] = format_attributes_to_string(
        get_nested_value(d, "face.chin.width", -1),
        get_nested_value(d, "face.chin.height", -1),
        get_nested_value(d, "face.chin.depth", -1),
        get_nested_value(d, "face.chin.angle", -1),
        get_nested_value(d, "face.chin.lower_height", -1),
        get_nested_value(d, "face.chin.tip_width", -1),
        get_nested_value(d, "face.chin.tip_height", -1),
        get_nested_value(d, "face.chin.tip_depth", -1)
    )

    # 痣
    result["f_mole"] = (
        f"{get_nested_value(d, 'face.mole.#name', '')} "
        f"{convert_rgba_to_hex_aa(get_nested_value(d, 'face.mole.color', ''))}"
        if not is_nashi('mole', get_nested_value(d, 'face.mole.id', -1))
        else ""
    )
    
    # 化妝 眼影
    result["f_mak_eye"] = (
        f"{get_nested_value(d, 'face.makeup.eyeshadow.#name', '')} "
        f"{convert_rgba_to_hex_aa(get_nested_value(d, 'face.makeup.eyeshadow.color', ''))}"
        if not is_nashi('eyeshadow', get_nested_value(d, 'face.makeup.eyeshadow.id', -1))
        else ""
    )
    
    # 腮紅
    result["f_mak_blu"] = (
        f"{get_nested_value(d, 'face.makeup.blush.#name', '')} "
        f"{convert_rgba_to_hex_aa(get_nested_value(d, 'face.makeup.blush.color', ''))}"
        if not is_nashi('blush', get_nested_value(d, 'face.makeup.blush.id', -1))
        else ""
    )
    
    # 唇膏
    result["f_mak_lip"] = (
        f"{get_nested_value(d, 'face.makeup.lipstick.#name', '')} "
        f"{convert_rgba_to_hex_aa(get_nested_value(d, 'face.makeup.lipstick.color', ''))}"
        if not is_nashi('lipstick', get_nested_value(d, 'face.makeup.lipstick.id', -1))
        else ""
    )

    # 刺青
    result["f_tattoo"] = (
        f"{get_nested_value(d, 'face.tattoo.#name', '')} "
        f"{convert_rgba_to_hex_aa(get_nested_value(d, 'face.tattoo.color', ''))}"
        if not is_nashi('tattoo', get_nested_value(d, 'face.tattoo.id', -1))
        else ""
    )
    
    return result
