# your_character_project/parsers/face_parser.py

from io import BytesIO
from common_types import (
    _read_uint32, _read_int32, _read_float, _read_bytes_as_hex,
    _read_and_format_to_value,
    _read_and_format_color,
)
import json
from game_data.face_data import get_face_by_id

# UI 界面整理的格式
ui_category = ['overall', 'ears', 'eyebrows', 'eyelashes',
               'eyes', 'eyeballs', 'nose', 'cheeks',
               'mouth', 'chin', 'mole', 'makeup',
               'tattoo']

def parse_face_data(stream: BytesIO, debug_mode: bool = False) -> dict:
    """
    解析角色的臉部數據。
    Args:
        stream: 包含角色二進位資料的 BytesIO 串流物件。
        debug_mode: 是否開啟除錯模式，印出詳細解析過程。
    Returns:
        一個字典，包含解析後的臉部數據。
    """
    face_data = {key: {} for key in ui_category}
    
    current_pos = 0
    if debug_mode:
        current_pos = stream.tell()
        print(f"  [Offset: {current_pos}] Starting to parse face data.")

    try:
        # -- Overall Face 全體 2 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Overall Face' data.")
        contour_id = _read_int32(stream)
        contour_name = get_face_by_id('contour', contour_id)
        muscle_id = _read_int32(stream)
        muscle_name = get_face_by_id('muscle', muscle_id)
        wrinkle_id = _read_int32(stream)
        wrinkle_name = get_face_by_id('wrinkle', wrinkle_id)
        temp_overall = {
            'contour_id': contour_id, # 輪廓 ID
            '#contour_name': contour_name,
            'muscle_id': muscle_id,  # 肌肉 ID
            '#muscle_name': muscle_name,
            'wrinkle_id': wrinkle_id, # 皺紋 ID (陰影)
            '#wrinkle_name': wrinkle_name,
            'wrinkle_depth': _read_and_format_to_value(stream), # 皺紋深度 (シワの深さ)
        }

        # -- Eyebrows 眉毛 2--
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Eyebrows' data.")
        eyebrows_id = _read_int32(stream)#(_read_int32(stream), _read_int32(stream))
        temp_eyebrows = {
            'id': eyebrows_id,#f'({eyebrows_id[0]}, {eyebrows_id[1]})', # 眉毛形狀 ID
            'extra': _read_int32(stream), # 應該是 2
            '#name': get_face_by_id('eyebrows', eyebrows_id),
            'color': _read_and_format_color(stream), # 眉毛顏色 (RGBA)
            '!shine' : _read_and_format_color(stream), # 可能有一個光澤顏色 (RGBA) 但不能改 似乎是 (205,205,205,255)
            'strength': _read_and_format_to_value(stream), # 光澤強度
            'texture': _read_and_format_to_value(stream),  # 光澤質感
        }

        # -- Eyeballs (Left Eye) 眼球 (左眼) --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Eyeballs (Left Eye)' data.")
        pupil_id = _read_int32(stream)
        temp_left_eyeball = {
            'pupil_id': pupil_id,       # 左瞳 ID
            '#name': get_face_by_id('eyeball', pupil_id),
            'sclera_color': _read_and_format_color(stream), # 左眼白顏色 (RGBA, alpha 無效)
            'pupil_color': _read_and_format_color(stream),  # 左瞳孔顏色 (RGBA, alpha 無效)
            'pupil_size': _read_and_format_to_value(stream),     # 左瞳孔大小
            'pupil_brightness': _read_and_format_to_value(stream), # 左瞳孔亮度
        }

        # -- Eyeballs (Right Eye) 眼球 (右眼) --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Eyeballs (Right Eye)' data.")
        pupil_id = _read_int32(stream)
        temp_right_eyeball = {
            'pupil_id': pupil_id,       # 右瞳 ID
            '#name': get_face_by_id('eyeball', pupil_id),
            'sclera_color': _read_and_format_color(stream), # 右眼白顏色 (RGBA, alpha 無效)
            'pupil_color': _read_and_format_color(stream),  # 右瞳孔顏色 (RGBA, alpha 無效)
            'pupil_size': _read_and_format_to_value(stream),     # 右瞳孔大小
            'pupil_brightness': _read_and_format_to_value(stream), # 右瞳孔亮度
        }

        # -- Tattoo 刺青 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Tattoo' data.")
        tattoo_id = _read_int32(stream)
        face_data['tattoo'] = {
            'id': tattoo_id,      # 刺青 ID
            '#name': get_face_by_id('tattoo', tattoo_id),
            'color': _read_and_format_color(stream), # 刺青顏色 (RGBA, alpha 無效)
            # 0x43 0x00 0x00 0x00 感覺是跟著 Tattoo 的
            '!padding': _read_bytes_as_hex(stream, 4) # 從 0x018E 到 0x0192，中間有 4 個 bytes 的空位
        }

        # -- Overall Face 全體 1 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Face Dimensions' data.")
        face_data['overall'] = {
            'overall_width': _read_and_format_to_value(stream), # 全體橫幅
            'upper_part_depth': _read_and_format_to_value(stream), # 上部前後
            'upper_part_height': _read_and_format_to_value(stream), # 上部上下
            'lower_part_depth': _read_and_format_to_value(stream), # 下部前後
            'lower_part_width': _read_and_format_to_value(stream), # 下部橫幅
        } | temp_overall

        # -- Chin 下巴 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Chin' data.")
        face_data['chin'] = {
            'width': _read_and_format_to_value(stream),    # 橫幅
            'height': _read_and_format_to_value(stream),   # 上下
            'depth': _read_and_format_to_value(stream),    # 前後
            'angle': _read_and_format_to_value(stream),    # 角度
            'lower_height': _read_and_format_to_value(stream), # 下部上下
            'tip_width': _read_and_format_to_value(stream),  # 先幅 (下巴尖端寬度)
            'tip_height': _read_and_format_to_value(stream), # 先上下 (下巴尖端上下)
            'tip_depth': _read_and_format_to_value(stream),  # 先前後 (下巴尖端前後)
        }

        # -- Cheeks 頰 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Cheeks' data.")
        face_data['cheeks'] = {
            'lower_height': _read_and_format_to_value(stream), # 下部上下
            'lower_depth': _read_and_format_to_value(stream),  # 下部前後
            'lower_width': _read_and_format_to_value(stream),  # 下部幅
            'upper_height': _read_and_format_to_value(stream), # 上部上下
            'upper_depth': _read_and_format_to_value(stream),  # 上部前後
            'upper_width': _read_and_format_to_value(stream),  # 上部幅
        }

        # -- Eyebrows 眉毛 1-- (眉弓骨/眉毛位置的調整)
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Brow' data.")
        face_data['eyebrows'] = {
            'height': _read_and_format_to_value(stream),     # 上下
            'horizontal_position': _read_and_format_to_value(stream), # 橫位置
            'angle_z': _read_and_format_to_value(stream),   # 角度Z軸
            'inner_shape': _read_and_format_to_value(stream), # 內側形狀
            'outer_shape': _read_and_format_to_value(stream), # 外側形狀
        } | temp_eyebrows
        
        

        # -- Eyes 目元 -- (眼周區域，包含眼裂、眼角等)
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Eyes' data.")
        face_data['eyes'] = {
            'height': _read_and_format_to_value(stream),         # 上下
            'horizontal_position': _read_and_format_to_value(stream), # 橫位置
            'depth': _read_and_format_to_value(stream),          # 前後
            'width': _read_and_format_to_value(stream),          # 橫幅
            'vertical_width': _read_and_format_to_value(stream), # 縱幅
            'angle_z': _read_and_format_to_value(stream),       # 角度Z軸
            'angle_y': _read_and_format_to_value(stream),       # 角度Y軸
            'inner_corner_h_pos': _read_and_format_to_value(stream), # 目頭左右位置
            'outer_corner_h_pos': _read_and_format_to_value(stream), # 目尻左右位置
            'inner_corner_v_pos': _read_and_format_to_value(stream), # 目頭上下位置
            'outer_corner_v_pos': _read_and_format_to_value(stream), # 目尻上下位置
            'eyelid_shape_1': _read_and_format_to_value(stream), # 眼瞼形狀1
            'eyelid_shape_2': _read_and_format_to_value(stream), # 眼瞼形狀2
        }

        # -- Eyeballs (Basic Settings) 眼球 (基本設定) --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Eyeballs (Basic Settings)' data.")
        face_data['eyeballs'] = {
            'pupil_v_adjustment': _read_and_format_to_value(stream), # 瞳的上下調整
            'pupil_width': _read_and_format_to_value(stream),    # 瞳的橫幅
            'pupil_vertical_width': _read_and_format_to_value(stream), # 瞳的縱幅
        }
        # add left eyeball and right eyeball| temp_left_eye | temp_right_eye
        face_data['eyeballs']['left_eyeball'] = temp_left_eyeball
        face_data['eyeballs']['right_eyeball'] = temp_right_eyeball

        # -- Nose 鼻 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Nose' data.")
        face_data['nose'] = {
            'overall_height': _read_and_format_to_value(stream),    # 全体上下
            'overall_depth': _read_and_format_to_value(stream),     # 全体前後
            'overall_angle_x': _read_and_format_to_value(stream),   # 全体角度X軸
            'overall_width': _read_and_format_to_value(stream),     # 全体橫幅
            'bridge_height': _read_and_format_to_value(stream),     # 鼻筋高度
            'bridge_width': _read_and_format_to_value(stream),      # 鼻筋橫幅
            'bridge_shape': _read_and_format_to_value(stream),      # 鼻筋形狀
            'nostril_width': _read_and_format_to_value(stream),     # 小鼻橫幅
            'nostril_height': _read_and_format_to_value(stream),    # 小鼻上下
            'nostril_depth': _read_and_format_to_value(stream),     # 小鼻前後
            'nostril_angle_x': _read_and_format_to_value(stream),   # 小鼻角度X軸
            'nostril_angle_z': _read_and_format_to_value(stream),   # 小鼻角度Z軸
            'tip_height': _read_and_format_to_value(stream),        # 鼻尖高度
            'tip_angle_x': _read_and_format_to_value(stream),       # 鼻尖角度X軸
            'tip_size': _read_and_format_to_value(stream),          # 鼻尖大小
        }

        # -- Mouth 口 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Mouth' data.")
        face_data['mouth'] = {
            'height': _read_and_format_to_value(stream),      # 上下
            'width': _read_and_format_to_value(stream),       # 橫幅
            'vertical_width': _read_and_format_to_value(stream), # 縱幅
            'depth': _read_and_format_to_value(stream),       # 前後
            'upper_lip_shape': _read_and_format_to_value(stream), # 形狀上
            'lower_lip_shape': _read_and_format_to_value(stream), # 形狀下
            'corner_shape': _read_and_format_to_value(stream), # 形狀口角
        }

        # -- Ear 耳 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Ear' data.")
        face_data['ears'] = {
            'size': _read_and_format_to_value(stream),         # size
            'angle_y': _read_and_format_to_value(stream),      # 角度Y軸
            'angle_z': _read_and_format_to_value(stream),      # 角度Z軸
            'upper_shape': _read_and_format_to_value(stream),  # 上部形狀
            'lower_shape': _read_and_format_to_value(stream),  # 下部形狀
        }

        # -- Eyelashes 睫毛 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Eyelashes' data.")
        eyelashes_id = _read_int32(stream) #(_read_int32(stream), _read_int32(stream))
        face_data['eyelashes'] = {
            'id': eyelashes_id, # f"({eyelashes_id[0]}, {eyelashes_id[1]})", # 睫毛 ID
            'extra': _read_int32(stream), # always be 2
            '#name': get_face_by_id('eyelashes', eyelashes_id),
            'color': _read_and_format_color(stream), # 睫毛顏色 (RGBA)
            '!shine': _read_and_format_color(stream), # 睫毛光澤顏色 (RGBA) (185, 188, 177, 255) ??? 這個值會一直跳來跳去..
            'strength': _read_and_format_to_value(stream), # 光澤強度
            'texture': _read_and_format_to_value(stream),  # 光澤質感
        }

        # -- Eyeshadow 眼影 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Eyeshadow' data.")
        eyeshadow_id = _read_int32(stream)
        face_data['makeup']['eyeshadow'] = {
            'id': eyeshadow_id,   # 眼影 ID
            '#name': get_face_by_id('eyeshadow', eyeshadow_id),
            'color': _read_and_format_color(stream), # 眼影顏色 (RGBA, alpha 無效)
        }
        
        # -- Blush 腮紅 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Blush' data.")
        blush_id = _read_int32(stream)
        face_data['makeup']['blush'] = {
            'id': blush_id,       # 腮紅 ID
            '#name': get_face_by_id('blush', blush_id),
            'color': _read_and_format_color(stream), # 腮紅顏色 (RGBA, alpha 無效)
        }

        # -- Lipstick 唇膏 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Lipstick' data.")
        lipstick_id = _read_int32(stream)
        face_data['makeup']['lipstick'] = {
            'id': lipstick_id,    # 唇膏 ID
            '#name': get_face_by_id('lipstick', lipstick_id),
            'color': _read_and_format_color(stream), # 唇膏顏色 (RGBA, alpha 無效)
        }

        # -- Mole 痣 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Mole' data.")
        mole_id = _read_int32(stream)
        face_data['mole'] = {
            'id': mole_id,        # 痣 ID
            '#name': get_face_by_id('mole', mole_id),
            'color': _read_and_format_color(stream), # 痣顏色 (RGBA, alpha 無效)
        }

        # -- Eyeballs (Highlight) 眼球 (高光) --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Eyeballs (Highlight)' data.")
        highlight_id = _read_int32(stream) # (_read_int32(stream), _read_int32(stream))
        face_data['eyeballs'].update(
            {
                'highlight_id': highlight_id, # f"({highlight_id[0]}, {highlight_id[1]})", # 高光 ID
                'highlight_extra': _read_int32(stream), # always be 7
                '#name': get_face_by_id('highlight', highlight_id),
                'highlight_color': _read_and_format_color(stream), # 高光顏色 (RGBA)
                '!highlight_shine': _read_and_format_color(stream), # 高光光澤?!
                '!highlight_strength': _read_and_format_to_value(stream),
                '!highlight_texture': _read_and_format_to_value(stream),
                
            }
        )

    except EOFError as e:
        if debug_mode:
            print(f"    [ERROR] Stream ended prematurely when parsing face data: {e}")
        raise
    except Exception as e:
        if debug_mode:
            print(f"    [ERROR] Unknown error occurred when parsing face data: {e}")
        raise

    if debug_mode:
        print(f"  Face data parsing complete. Next read position: {stream.tell()}")
        try:
            json_output = json.dumps(face_data, indent=2, ensure_ascii=False)
            print("\n  --- Face Parser JSON Debug Output ---")
            print(json_output)
            print("  -----------------------------------\n")
        except TypeError as json_e:
            print(f"\n  [CRITICAL ERROR] Face parser returned data cannot be JSON serialized: {json_e}")
            problematic_types = []
            def find_unserializable_in_dict(d):
                for k, v in d.items():
                    if isinstance(v, (bytes, bytearray)):
                        problematic_types.append(f"Key '{k}': {type(v)}")
                    elif isinstance(v, dict):
                        find_unserializable_in_dict(v)
            find_unserializable_in_dict(face_data)
            print(f"  Unserializable data types: {problematic_types}")
            print("  -----------------------------------\n")

    return face_data