# ph-editor/serializers/face_serializer.py

from io import BytesIO
import struct
from utils.common_types import (
    _pack_uint32, _pack_int32, _pack_float, _pack_color,
    _parse_and_pack_float,
    _pack_hex_to_bytes,
)

    
def serialize_face_data(face_data: dict, stream: BytesIO):
    """
    序列化臉部數據。
    Args:
        face_data: 包含臉部數據的字典。
        stream: BytesIO 串流物件，用於寫入位元組。
    """
    current_pos = stream.tell()
    #print(f"    [偏移: {current_pos}] 開始序列化臉部數據。")

    try:
        # --- Overall Face 全體 2 ---
        if 'overall' in face_data:
            overall = face_data['overall']
            stream.write(_pack_int32(overall.get('contour_id', 0)))
            stream.write(_pack_int32(overall.get('muscle_id', 0)))
            stream.write(_pack_int32(overall.get('wrinkle_id', 0)))
            stream.write(_parse_and_pack_float(overall.get('wrinkle_depth', 0)))

        # --- Eyebrows 眉毛 2 ---
        if 'eyebrows' in face_data:
            eyebrows = face_data['eyebrows']
            stream.write(_pack_int32(eyebrows.get('id', 0))) # eyebrows id
            stream.write(_pack_int32(eyebrows.get('extra', 2))) # always 2
            stream.write(_pack_color(eyebrows.get('color', (0,0,0,255))))
            stream.write(_pack_color(eyebrows.get('!shine', (205,205,205,255)))) # Assuming default for !shine_color
            stream.write(_parse_and_pack_float(eyebrows.get('strength', 0)))
            stream.write(_parse_and_pack_float(eyebrows.get('texture', 0)))

        # --- Eyeballs (Left Eye) 眼球 (左眼) ---
        if 'eyeballs' in face_data and 'left_eyeball' in face_data['eyeballs']:
            left_eyeball = face_data['eyeballs']['left_eyeball']
            stream.write(_pack_int32(left_eyeball.get('pupil_id', 0)))
            stream.write(_pack_color(left_eyeball.get('sclera_color', (255,255,255,255))))
            stream.write(_pack_color(left_eyeball.get('pupil_color', (0,0,0,255))))
            stream.write(_parse_and_pack_float(left_eyeball.get('pupil_size', 0)))
            stream.write(_parse_and_pack_float(left_eyeball.get('pupil_brightness', 0)))

        # --- Eyeballs (Right Eye) 眼球 (右眼) ---
        if 'eyeballs' in face_data and 'right_eyeball' in face_data['eyeballs']:
            right_eyeball = face_data['eyeballs']['right_eyeball']
            stream.write(_pack_int32(right_eyeball.get('pupil_id', 0)))
            stream.write(_pack_color(right_eyeball.get('sclera_color', (255,255,255,255))))
            stream.write(_pack_color(right_eyeball.get('pupil_color', (0,0,0,255))))
            stream.write(_parse_and_pack_float(right_eyeball.get('pupil_size', 0)))
            stream.write(_parse_and_pack_float(right_eyeball.get('pupil_brightness', 0)))

        # --- Tattoo 刺青 ---
        if 'tattoo' in face_data:
            tattoo = face_data['tattoo']
            stream.write(_pack_int32(tattoo.get('id', 0)))
            stream.write(_pack_color(tattoo.get('color', (255,255,255,255))))
            stream.write(_pack_hex_to_bytes(tattoo.get('!padding', '43 00 00 00'), 4)) # Assuming padding is hex string

        # --- Overall Face 全體 1 ---
        if 'overall' in face_data:
            overall = face_data['overall']
            stream.write(_parse_and_pack_float(overall.get('overall_width', 0)))
            stream.write(_parse_and_pack_float(overall.get('upper_part_depth', 0)))
            stream.write(_parse_and_pack_float(overall.get('upper_part_height', 0)))
            stream.write(_parse_and_pack_float(overall.get('lower_part_depth', 0)))
            stream.write(_parse_and_pack_float(overall.get('lower_part_width', 0)))

        # --- Chin 下巴 ---
        if 'chin' in face_data:
            chin = face_data['chin']
            stream.write(_parse_and_pack_float(chin.get('width', 0)))
            stream.write(_parse_and_pack_float(chin.get('height', 0)))
            stream.write(_parse_and_pack_float(chin.get('depth', 0)))
            stream.write(_parse_and_pack_float(chin.get('angle', 0)))
            stream.write(_parse_and_pack_float(chin.get('lower_height', 0)))
            stream.write(_parse_and_pack_float(chin.get('tip_width', 0)))
            stream.write(_parse_and_pack_float(chin.get('tip_height', 0)))
            stream.write(_parse_and_pack_float(chin.get('tip_depth', 0)))

        # --- Cheeks 頰 ---
        if 'cheeks' in face_data:
            cheeks = face_data['cheeks']
            stream.write(_parse_and_pack_float(cheeks.get('lower_height', 0)))
            stream.write(_parse_and_pack_float(cheeks.get('lower_depth', 0)))
            stream.write(_parse_and_pack_float(cheeks.get('lower_width', 0)))
            stream.write(_parse_and_pack_float(cheeks.get('upper_height', 0)))
            stream.write(_parse_and_pack_float(cheeks.get('upper_depth', 0)))
            stream.write(_parse_and_pack_float(cheeks.get('upper_width', 0)))

        # --- Eyebrows 眉毛 1 ---
        # Note: 'eyebrows' category combines data from two sections in parser.
        # Ensure we write only the 'eyebrows 1' specific floats here.
        if 'eyebrows' in face_data:
            eyebrows = face_data['eyebrows']
            stream.write(_parse_and_pack_float(eyebrows.get('height', 0)))
            stream.write(_parse_and_pack_float(eyebrows.get('horizontal_position', 0)))
            stream.write(_parse_and_pack_float(eyebrows.get('angle_z', 0)))
            stream.write(_parse_and_pack_float(eyebrows.get('inner_shape', 0)))
            stream.write(_parse_and_pack_float(eyebrows.get('outer_shape', 0)))
        
        # --- Eyes 目元 ---
        if 'eyes' in face_data:
            eyes = face_data['eyes']
            stream.write(_parse_and_pack_float(eyes.get('height', 0)))
            stream.write(_parse_and_pack_float(eyes.get('horizontal_position', 0)))
            stream.write(_parse_and_pack_float(eyes.get('depth', 0)))
            stream.write(_parse_and_pack_float(eyes.get('width', 0)))
            stream.write(_parse_and_pack_float(eyes.get('vertical_width', 0)))
            stream.write(_parse_and_pack_float(eyes.get('angle_z', 0)))
            stream.write(_parse_and_pack_float(eyes.get('angle_y', 0)))
            stream.write(_parse_and_pack_float(eyes.get('inner_corner_h_pos', 0)))
            stream.write(_parse_and_pack_float(eyes.get('outer_corner_h_pos', 0)))
            stream.write(_parse_and_pack_float(eyes.get('inner_corner_v_pos', 0)))
            stream.write(_parse_and_pack_float(eyes.get('outer_corner_v_pos', 0)))
            stream.write(_parse_and_pack_float(eyes.get('eyelid_shape_1', 0)))
            stream.write(_parse_and_pack_float(eyes.get('eyelid_shape_2', 0)))

        # --- Eyeballs (Basic Settings) 眼球 (基本設定) ---
        if 'eyeballs' in face_data:
            eyeballs = face_data['eyeballs']
            stream.write(_parse_and_pack_float(eyeballs.get('pupil_v_adjustment', 0)))
            stream.write(_parse_and_pack_float(eyeballs.get('pupil_width', 0)))
            stream.write(_parse_and_pack_float(eyeballs.get('pupil_vertical_width', 0)))

        # --- Nose 鼻 ---
        if 'nose' in face_data:
            nose = face_data['nose']
            stream.write(_parse_and_pack_float(nose.get('overall_height', 0)))
            stream.write(_parse_and_pack_float(nose.get('overall_depth', 0)))
            stream.write(_parse_and_pack_float(nose.get('overall_angle_x', 0)))
            stream.write(_parse_and_pack_float(nose.get('overall_width', 0)))
            stream.write(_parse_and_pack_float(nose.get('bridge_height', 0)))
            stream.write(_parse_and_pack_float(nose.get('bridge_width', 0)))
            stream.write(_parse_and_pack_float(nose.get('bridge_shape', 0)))
            stream.write(_parse_and_pack_float(nose.get('nostril_width', 0)))
            stream.write(_parse_and_pack_float(nose.get('nostril_height', 0)))
            stream.write(_parse_and_pack_float(nose.get('nostril_depth', 0)))
            stream.write(_parse_and_pack_float(nose.get('nostril_angle_x', 0)))
            stream.write(_parse_and_pack_float(nose.get('nostril_angle_z', 0)))
            stream.write(_parse_and_pack_float(nose.get('tip_height', 0)))
            stream.write(_parse_and_pack_float(nose.get('tip_angle_x', 0)))
            stream.write(_parse_and_pack_float(nose.get('tip_size', 0)))

        # --- Mouth 口 ---
        if 'mouth' in face_data:
            mouth = face_data['mouth']
            stream.write(_parse_and_pack_float(mouth.get('height', 0)))
            stream.write(_parse_and_pack_float(mouth.get('width', 0)))
            stream.write(_parse_and_pack_float(mouth.get('vertical_width', 0)))
            stream.write(_parse_and_pack_float(mouth.get('depth', 0)))
            stream.write(_parse_and_pack_float(mouth.get('upper_lip_shape', 0)))
            stream.write(_parse_and_pack_float(mouth.get('lower_lip_shape', 0)))
            stream.write(_parse_and_pack_float(mouth.get('corner_shape', 0)))

        # --- Ear 耳 ---
        if 'ears' in face_data:
            ears = face_data['ears']
            stream.write(_parse_and_pack_float(ears.get('size', 0)))
            stream.write(_parse_and_pack_float(ears.get('angle_y', 0)))
            stream.write(_parse_and_pack_float(ears.get('angle_z', 0)))
            stream.write(_parse_and_pack_float(ears.get('upper_shape', 0)))
            stream.write(_parse_and_pack_float(ears.get('lower_shape', 0)))

        # --- Eyelashes 睫毛 ---
        if 'eyelashes' in face_data:
            eyelashes = face_data['eyelashes']
            stream.write(_pack_int32(eyelashes.get('id', 0)))
            stream.write(_pack_int32(eyelashes.get('extra', 2)))
            stream.write(_pack_color(eyelashes.get('color', (0,0,0,255))))
            stream.write(_pack_color(eyelashes.get('!shine', (185,188,177,255)))) # Assuming default for !shine_color
            stream.write(_parse_and_pack_float(eyelashes.get('strength', 0)))
            stream.write(_parse_and_pack_float(eyelashes.get('texture', 0)))

        # --- Eyeshadow 眼影 ---
        if 'makeup' in face_data and 'eyeshadow' in face_data['makeup']:
            eyeshadow = face_data['makeup']['eyeshadow']
            stream.write(_pack_int32(eyeshadow.get('id', 0)))
            stream.write(_pack_color(eyeshadow.get('color', (255,255,255,255))))

        # --- Blush 腮紅 ---
        if 'makeup' in face_data and 'blush' in face_data['makeup']:
            blush = face_data['makeup']['blush']
            stream.write(_pack_int32(blush.get('id', 0)))
            stream.write(_pack_color(blush.get('color', (255,255,255,255))))

        # --- Lipstick 唇膏 ---
        if 'makeup' in face_data and 'lipstick' in face_data['makeup']:
            lipstick = face_data['makeup']['lipstick']
            stream.write(_pack_int32(lipstick.get('id', 0)))
            stream.write(_pack_color(lipstick.get('color', (255,255,255,255))))

        # --- Mole 痣 ---
        if 'mole' in face_data:
            mole = face_data['mole']
            stream.write(_pack_int32(mole.get('id', 0)))
            stream.write(_pack_color(mole.get('color', (255,255,255,255))))

        # --- Eyeballs (Highlight) 眼球 (高光) ---
        if 'eyeballs' in face_data:
            eyeballs = face_data['eyeballs']
            stream.write(_pack_int32(eyeballs.get('highlight_id', 0)))
            stream.write(_pack_int32(eyeballs.get('highlight_extra', 7)))
            stream.write(_pack_color(eyeballs.get('highlight_color', (255,255,255,255))))
            stream.write(_pack_color(eyeballs.get('!highlight_shine', (255,255,255,255)))) # Assuming default for !highlight_shine
            stream.write(_parse_and_pack_float(eyeballs.get('!highlight_strength', 0)))
            stream.write(_parse_and_pack_float(eyeballs.get('!highlight_texture', 0)))

    except Exception as e:
        print(f"    [錯誤] 序列化臉部數據時發生未知錯誤: {e}")
        raise

    #print(f"    臉部數據序列化完成。下一個寫入位置: {stream.tell()}")