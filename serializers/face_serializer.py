# ph-editor/serializers/face_serializer.py

from io import BytesIO
import struct
from common_types import (
    _pack_uint32, _pack_int32, _pack_float, _pack_color,
    _parse_and_pack_float,    
)
# 假設 common_types 提供以下打包函數
# 如果您的 common_types 實際提供這些，可以直接導入
# 這裡為示範目的提供簡易實現
def _pack_uint32(value: int) -> bytes:
    return struct.pack('<I', value)

def _pack_int32(value: int) -> bytes:
    return struct.pack('<i', value)

def _pack_float(value: float) -> bytes:
    return struct.pack('<f', value)

def _pack_color(rgba: tuple[int, int, int, int]) -> bytes:
    """Pack RGBA color (4 bytes: R, G, B, A)"""
    return bytes(rgba)

def _pack_hex_bytes(hex_str: str, length: int) -> bytes:
    """Pack a hexadecimal string representation of bytes."""
    # 確保 hex_str 是偶數長度
    if len(hex_str) % 2 != 0:
        hex_str = '0' + hex_str
    # 從十六進制字符串轉換為字節
    packed_bytes = bytes.fromhex(hex_str)
    # 確保長度符合預期，如果不足則填充 0x00，如果超出則截斷
    if len(packed_bytes) < length:
        packed_bytes += b'\x00' * (length - len(packed_bytes))
    return packed_bytes[:length]

def _format_percentage_to_float(value: int, scale: float = 100) -> float:
    """
    將 0-100% 的整數值轉換為浮點數。
    """
    return float(value) / scale

def serialize_face_data(face_data: dict, stream: BytesIO):
    """
    序列化臉部數據。
    Args:
        face_data: 包含臉部數據的字典。
        stream: BytesIO 串流物件，用於寫入位元組。
    """
    current_pos = stream.tell()
    print(f"    [偏移: {current_pos}] 開始序列化臉部數據。")

    try:
        # --- Overall Face 全體 2 ---
        if 'overall' in face_data:
            overall = face_data['overall']
            stream.write(_pack_int32(overall.get('contour_id', 0)))
            stream.write(_pack_int32(overall.get('muscle_id', 0)))
            stream.write(_pack_int32(overall.get('wrinkle_id', 0)))
            stream.write(_pack_float(_format_percentage_to_float(overall.get('wrinkle_depth', 0))))

        # --- Eyebrows 眉毛 2 ---
        if 'eyebrows' in face_data:
            eyebrows = face_data['eyebrows']
            # eyebrows_id is a string like "(X, Y)", need to parse it back to tuple
            eyebrows_id_str = eyebrows.get('eyebrows_id', "(0, 2)")
            try:
                # Safely evaluate tuple string
                eyebrows_id_tuple = eval(eyebrows_id_str)
                stream.write(_pack_int32(eyebrows_id_tuple[0]))
                stream.write(_pack_int32(eyebrows_id_tuple[1]))
            except (SyntaxError, TypeError):
                print(f"[WARN] Invalid eyebrows_id format: {eyebrows_id_str}. Using default (0, 2).")
                stream.write(_pack_int32(0)) # Default first part of ID
                stream.write(_pack_int32(2)) # Default second part of ID

            stream.write(_pack_color(eyebrows.get('eyebrow_color', (0,0,0,255))))
            stream.write(_pack_color(eyebrows.get('!shine_color', (205,205,205,255)))) # Assuming default for !shine_color
            stream.write(_pack_float(_format_percentage_to_float(eyebrows.get('shine_strength', 0))))
            stream.write(_pack_float(_format_percentage_to_float(eyebrows.get('shine_texture', 0))))

        # --- Eyeballs (Left Eye) 眼球 (左眼) ---
        if 'eyeballs' in face_data and 'left_eyeball' in face_data['eyeballs']:
            left_eyeball = face_data['eyeballs']['left_eyeball']
            stream.write(_pack_int32(left_eyeball.get('pupil_id', 0)))
            stream.write(_pack_color(left_eyeball.get('sclera_color', (255,255,255,255))))
            stream.write(_pack_color(left_eyeball.get('pupil_color', (0,0,0,255))))
            stream.write(_pack_float(_format_percentage_to_float(left_eyeball.get('pupil_size', 0))))
            stream.write(_pack_float(_format_percentage_to_float(left_eyeball.get('pupil_brightness', 0))))

        # --- Eyeballs (Right Eye) 眼球 (右眼) ---
        if 'eyeballs' in face_data and 'right_eyeball' in face_data['eyeballs']:
            right_eyeball = face_data['eyeballs']['right_eyeball']
            stream.write(_pack_int32(right_eyeball.get('pupil_id', 0)))
            stream.write(_pack_color(right_eyeball.get('sclera_color', (255,255,255,255))))
            stream.write(_pack_color(right_eyeball.get('pupil_color', (0,0,0,255))))
            stream.write(_pack_float(_format_percentage_to_float(right_eyeball.get('pupil_size', 0))))
            stream.write(_pack_float(_format_percentage_to_float(right_eyeball.get('pupil_brightness', 0))))

        # --- Tattoo 刺青 ---
        if 'tattoo' in face_data:
            tattoo = face_data['tattoo']
            stream.write(_pack_int32(tattoo.get('id', 0)))
            stream.write(_pack_color(tattoo.get('color', (255,255,255,255))))
            stream.write(_pack_hex_bytes(tattoo.get('!padding', '00000000'), 4)) # Assuming padding is hex string

        # --- Overall Face 全體 1 ---
        if 'overall' in face_data:
            overall = face_data['overall']
            stream.write(_pack_float(_format_percentage_to_float(overall.get('overall_width', 0))))
            stream.write(_pack_float(_format_percentage_to_float(overall.get('upper_part_depth', 0))))
            stream.write(_pack_float(_format_percentage_to_float(overall.get('upper_part_height', 0))))
            stream.write(_pack_float(_format_percentage_to_float(overall.get('lower_part_depth', 0))))
            stream.write(_pack_float(_format_percentage_to_float(overall.get('lower_part_width', 0))))

        # --- Chin 下巴 ---
        if 'chin' in face_data:
            chin = face_data['chin']
            stream.write(_pack_float(_format_percentage_to_float(chin.get('width', 0))))
            stream.write(_pack_float(_format_percentage_to_float(chin.get('height', 0))))
            stream.write(_pack_float(_format_percentage_to_float(chin.get('depth', 0))))
            stream.write(_pack_float(_format_percentage_to_float(chin.get('angle', 0))))
            stream.write(_pack_float(_format_percentage_to_float(chin.get('lower_height', 0))))
            stream.write(_pack_float(_format_percentage_to_float(chin.get('tip_width', 0))))
            stream.write(_pack_float(_format_percentage_to_float(chin.get('tip_height', 0))))
            stream.write(_pack_float(_format_percentage_to_float(chin.get('tip_depth', 0))))

        # --- Cheeks 頰 ---
        if 'cheeks' in face_data:
            cheeks = face_data['cheeks']
            stream.write(_pack_float(_format_percentage_to_float(cheeks.get('lower_height', 0))))
            stream.write(_pack_float(_format_percentage_to_float(cheeks.get('lower_depth', 0))))
            stream.write(_pack_float(_format_percentage_to_float(cheeks.get('lower_width', 0))))
            stream.write(_pack_float(_format_percentage_to_float(cheeks.get('upper_height', 0))))
            stream.write(_pack_float(_format_percentage_to_float(cheeks.get('upper_depth', 0))))
            stream.write(_pack_float(_format_percentage_to_float(cheeks.get('upper_width', 0))))

        # --- Eyebrows 眉毛 1 ---
        # Note: 'eyebrows' category combines data from two sections in parser.
        # Ensure we write only the 'eyebrows 1' specific floats here.
        if 'eyebrows' in face_data:
            eyebrows = face_data['eyebrows']
            stream.write(_pack_float(_format_percentage_to_float(eyebrows.get('height', 0))))
            stream.write(_pack_float(_format_percentage_to_float(eyebrows.get('horizontal_position', 0))))
            stream.write(_pack_float(_format_percentage_to_float(eyebrows.get('angle_z', 0))))
            stream.write(_pack_float(_format_percentage_to_float(eyebrows.get('inner_shape', 0))))
            stream.write(_pack_float(_format_percentage_to_float(eyebrows.get('outer_shape', 0))))

        # --- Eyes 目元 ---
        if 'eyes' in face_data:
            eyes = face_data['eyes']
            stream.write(_pack_float(_format_percentage_to_float(eyes.get('height', 0))))
            stream.write(_pack_float(_format_percentage_to_float(eyes.get('horizontal_position', 0))))
            stream.write(_pack_float(_format_percentage_to_float(eyes.get('depth', 0))))
            stream.write(_pack_float(_format_percentage_to_float(eyes.get('width', 0))))
            stream.write(_pack_float(_format_percentage_to_float(eyes.get('vertical_width', 0))))
            stream.write(_pack_float(_format_percentage_to_float(eyes.get('angle_z', 0))))
            stream.write(_pack_float(_format_percentage_to_float(eyes.get('angle_y', 0))))
            stream.write(_pack_float(_format_percentage_to_float(eyes.get('inner_corner_h_pos', 0))))
            stream.write(_pack_float(_format_percentage_to_float(eyes.get('outer_corner_h_pos', 0))))
            stream.write(_pack_float(_format_percentage_to_float(eyes.get('inner_corner_v_pos', 0))))
            stream.write(_pack_float(_format_percentage_to_float(eyes.get('outer_corner_v_pos', 0))))
            stream.write(_pack_float(_format_percentage_to_float(eyes.get('eyelid_shape_1', 0))))
            stream.write(_pack_float(_format_percentage_to_float(eyes.get('eyelid_shape_2', 0))))

        # --- Eyeballs (Basic Settings) 眼球 (基本設定) ---
        if 'eyeballs' in face_data:
            eyeballs = face_data['eyeballs']
            stream.write(_pack_float(_format_percentage_to_float(eyeballs.get('pupil_v_adjustment', 0))))
            stream.write(_pack_float(_format_percentage_to_float(eyeballs.get('pupil_width', 0))))
            stream.write(_pack_float(_format_percentage_to_float(eyeballs.get('pupil_vertical_width', 0))))

        # --- Nose 鼻 ---
        if 'nose' in face_data:
            nose = face_data['nose']
            stream.write(_pack_float(_format_percentage_to_float(nose.get('overall_height', 0))))
            stream.write(_pack_float(_format_percentage_to_float(nose.get('overall_depth', 0))))
            stream.write(_pack_float(_format_percentage_to_float(nose.get('overall_angle_x', 0))))
            stream.write(_pack_float(_format_percentage_to_float(nose.get('overall_width', 0))))
            stream.write(_pack_float(_format_percentage_to_float(nose.get('bridge_height', 0))))
            stream.write(_pack_float(_format_percentage_to_float(nose.get('bridge_width', 0))))
            stream.write(_pack_float(_format_percentage_to_float(nose.get('bridge_shape', 0))))
            stream.write(_pack_float(_format_percentage_to_float(nose.get('nostril_width', 0))))
            stream.write(_pack_float(_format_percentage_to_float(nose.get('nostril_height', 0))))
            stream.write(_pack_float(_format_percentage_to_float(nose.get('nostril_depth', 0))))
            stream.write(_pack_float(_format_percentage_to_float(nose.get('nostril_angle_x', 0))))
            stream.write(_pack_float(_format_percentage_to_float(nose.get('nostril_angle_z', 0))))
            stream.write(_pack_float(_format_percentage_to_float(nose.get('tip_height', 0))))
            stream.write(_pack_float(_format_percentage_to_float(nose.get('tip_angle_x', 0))))
            stream.write(_pack_float(_format_percentage_to_float(nose.get('tip_size', 0))))

        # --- Mouth 口 ---
        if 'mouth' in face_data:
            mouth = face_data['mouth']
            stream.write(_pack_float(_format_percentage_to_float(mouth.get('height', 0))))
            stream.write(_pack_float(_format_percentage_to_float(mouth.get('width', 0))))
            stream.write(_pack_float(_format_percentage_to_float(mouth.get('vertical_width', 0))))
            stream.write(_pack_float(_format_percentage_to_float(mouth.get('depth', 0))))
            stream.write(_pack_float(_format_percentage_to_float(mouth.get('upper_lip_shape', 0))))
            stream.write(_pack_float(_format_percentage_to_float(mouth.get('lower_lip_shape', 0))))
            stream.write(_pack_float(_format_percentage_to_float(mouth.get('corner_shape', 0))))

        # --- Ear 耳 ---
        if 'ears' in face_data:
            ears = face_data['ears']
            stream.write(_pack_float(_format_percentage_to_float(ears.get('size', 0))))
            stream.write(_pack_float(_format_percentage_to_float(ears.get('angle_y', 0))))
            stream.write(_pack_float(_format_percentage_to_float(ears.get('angle_z', 0))))
            stream.write(_pack_float(_format_percentage_to_float(ears.get('upper_shape', 0))))
            stream.write(_pack_float(_format_percentage_to_float(ears.get('lower_shape', 0))))

        # --- Eyelashes 睫毛 ---
        if 'eyelashes' in face_data:
            eyelashes = face_data['eyelashes']
            eyelash_id_str = eyelashes.get('eyelash_id', "(0, 2)")
            try:
                eyelash_id_tuple = eval(eyelash_id_str)
                stream.write(_pack_int32(eyelash_id_tuple[0]))
                stream.write(_pack_int32(eyelash_id_tuple[1]))
            except (SyntaxError, TypeError):
                print(f"[WARN] Invalid eyelash_id format: {eyelash_id_str}. Using default (0, 2).")
                stream.write(_pack_int32(0))
                stream.write(_pack_int32(2))

            stream.write(_pack_color(eyelashes.get('eyelash_color', (0,0,0,255))))
            stream.write(_pack_color(eyelashes.get('!shine_color', (185,188,177,255)))) # Assuming default for !shine_color
            stream.write(_pack_float(_format_percentage_to_float(eyelashes.get('shine_strength', 0))))
            stream.write(_pack_float(_format_percentage_to_float(eyelashes.get('shine_texture', 0))))

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
            highlight_id_str = eyeballs.get('highlight_id', "(0, 7)")
            try:
                highlight_id_tuple = eval(highlight_id_str)
                stream.write(_pack_int32(highlight_id_tuple[0]))
                stream.write(_pack_int32(highlight_id_tuple[1]))
            except (SyntaxError, TypeError):
                print(f"[WARN] Invalid highlight_id format: {highlight_id_str}. Using default (0, 7).")
                stream.write(_pack_int32(0))
                stream.write(_pack_int32(7))

            stream.write(_pack_color(eyeballs.get('highlight_color', (255,255,255,255))))
            stream.write(_pack_color(eyeballs.get('!highlight_shine', (255,255,255,255)))) # Assuming default for !highlight_shine
            stream.write(_pack_float(_format_percentage_to_float(eyeballs.get('!highlight_strength', 0))))
            stream.write(_pack_float(_format_percentage_to_float(eyeballs.get('!highlight_texture', 0))))

        # 檢查是否寫入了預期的總長度
        if stream.tell() != FACE_DATA_LENGTH:
            print(f"[WARN] 序列化長度不符。預期 {FACE_DATA_LENGTH} bytes，實際寫入 {stream.tell()} bytes。")
            # 可以在這裡選擇填充或截斷，但更重要的是檢查序列化邏輯是否正確
            # 為了確保文件結構一致性，如果實際寫入小於預期，則填充0
            if stream.tell() < FACE_DATA_LENGTH:
                stream.write(b'\x00' * (FACE_DATA_LENGTH - stream.tell()))
            elif stream.tell() > FACE_DATA_LENGTH:
                # 如果寫入過多，這通常表示序列化邏輯有誤，可能需要進一步除錯
                print(f"[ERROR] 實際寫入的資料長度 ({stream.tell()}) 超過預期長度 ({FACE_DATA_LENGTH})。")
                # 您可能需要調整 FACE_DATA_LENGTH 或重新檢查每個字段的寫入順序和大小

    except Exception as e:
        print(f"    [錯誤] 序列化臉部數據時發生未知錯誤: {e}")
        raise

    print(f"    臉部數據序列化完成。下一個寫入位置: {stream.tell()}")