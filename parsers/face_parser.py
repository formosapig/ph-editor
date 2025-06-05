# your_character_project/parsers/face_parser.py

from io import BytesIO
from common_types import (
    _read_uint32, _read_int32, _read_float, _read_color, format_color_for_json, _read_bytes_as_hex
)
import json
from game_data.face_data import get_face_by_id

# UI 界面整理的格式
ui_category = ['overall', 'ears', 'eyebrows', 'eyelashes',
               'eyes', 'eyeballs', 'nose', 'cheeks',
               'mouth', 'chin', 'mole', 'makeup',
               'tattoo']


# 新增一個函式來將浮點數轉換為百分比，並處理範圍限制
def _format_float_to_percentage(value: float, scale: float = 100, debug_mode: bool = False) -> int:
    """
    將浮點數轉換為 0-100% 的整數值。
    """
    percentage = round(value * scale)
    if debug_mode:
        # 為了保持與原JS註解一致，這裡仍然使用min/max來顯示調整範圍
        # 實際應用中，可以選擇是否強制限制輸出值在0-100之間
        if percentage < 0 or percentage > 100:
            print(f"    [WARN] Value {value} resulted in {percentage}%, clamped to [0, 100].")
    return max(0, min(100, percentage))


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
    
    if debug_mode:
        current_pos = stream.tell()
        print(f"  [Offset: {current_pos}] Starting to parse face data.")

    try:
        # 定位到臉部數據的起始位移 0x00E2
        # 注意: 這裡假設 stream 已經在正確的起始位置，
        # 如果不是，你可能需要 stream.seek(0x00E2)
        # 但在一個連續的解析流程中，通常會依序讀取
        
        # -- Overall Face 全體 2 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Overall Face' data.")
        contour_id = _read_int32(stream)
        contour_name = get_face_by_id('contour', contour_id)
        muscle_id = _read_int32(stream)
        muscle_name = get_face_by_id('muscle', muscle_id)
        temp_overall = {
            'contour_id': contour_id, # 輪廓 ID
            '#contour_name': contour_name,
            'muscle_id': muscle_id,  # 肌肉 ID
            '#muscle_name': muscle_name,
            'wrinkle_id': _read_uint32(stream), # 皺紋 ID (陰影)
            'wrinkle_depth': _format_float_to_percentage(_read_float(stream)), # 皺紋深度 (シワの深さ)
        }

        # -- Eyebrows 眉毛 2--
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Eyebrows' data.")
        temp_eyebrows = {
            'eyebrow_id': _read_uint32(stream), # 眉毛形狀 ID
            '!extra_value' : _read_uint32(stream), # extra value 看起來是 2
            'eyebrow_color': format_color_for_json(_read_color(stream)), # 眉毛顏色 (RGBA)
            '!shine_color' : format_color_for_json(_read_color(stream)), # 可能有一個光澤顏色 (RGBA) 但不能改 似乎是 (205,205,205,255)
            'shine_strength': _format_float_to_percentage(_read_float(stream)), # 光澤強度
            'shine_texture': _format_float_to_percentage(_read_float(stream)),  # 光澤質感
        }

        # -- Eyeballs (Left Eye) 眼球 (左眼) --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Eyeballs (Left Eye)' data.")
        temp_left_eye = {
            'left_pupil_id': _read_uint32(stream),       # 左瞳 ID
            'left_sclera_color': format_color_for_json(_read_color(stream)), # 左眼白顏色 (RGBA, alpha 無效)
            'left_pupil_color': format_color_for_json(_read_color(stream)),  # 左瞳孔顏色 (RGBA, alpha 無效)
            'left_pupil_size': _format_float_to_percentage(_read_float(stream)),     # 左瞳孔大小
            'left_pupil_brightness': _format_float_to_percentage(_read_float(stream)), # 左瞳孔亮度
        }

        # -- Eyeballs (Right Eye) 眼球 (右眼) --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Eyeballs (Right Eye)' data.")
        temp_right_eye = {
            'right_pupil_id': _read_uint32(stream),       # 右瞳 ID
            'right_sclera_color': format_color_for_json(_read_color(stream)), # 右眼白顏色 (RGBA, alpha 無效)
            'right_pupil_color': format_color_for_json(_read_color(stream)),  # 右瞳孔顏色 (RGBA, alpha 無效)
            'right_pupil_size': _format_float_to_percentage(_read_float(stream)),     # 右瞳孔大小
            'right_pupil_brightness': _format_float_to_percentage(_read_float(stream)), # 右瞳孔亮度
        }

        # -- Tattoo 刺青 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Tattoo' data.")
        face_data['tattoo'] = {
            'tattoo_id': _read_uint32(stream),      # 刺青 ID
            'tattoo_color': format_color_for_json(_read_color(stream)), # 刺青顏色 (RGBA, alpha 無效)
            # 0x43 0x00 0x00 0x00 感覺是跟著 Tattoo 的
            '!padding1': _read_bytes_as_hex(stream, 4) # 從 0x018E 到 0x0192，中間有 4 個 bytes 的空位
        }

        # -- Overall Face 全體 1 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Face Dimensions' data.")
        face_data['overall'] = {
            'overall_width': _format_float_to_percentage(_read_float(stream)), # 全體橫幅
            'upper_part_depth': _format_float_to_percentage(_read_float(stream)), # 上部前後
            'upper_part_height': _format_float_to_percentage(_read_float(stream)), # 上部上下
            'lower_part_depth': _format_float_to_percentage(_read_float(stream)), # 下部前後
            'lower_part_width': _format_float_to_percentage(_read_float(stream)), # 下部橫幅
        } | temp_overall

        # -- Chin 下巴 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Chin' data.")
        face_data['chin'] = {
            'width': _format_float_to_percentage(_read_float(stream)),    # 橫幅
            'height': _format_float_to_percentage(_read_float(stream)),   # 上下
            'depth': _format_float_to_percentage(_read_float(stream)),    # 前後
            'angle': _format_float_to_percentage(_read_float(stream)),    # 角度
            'lower_height': _format_float_to_percentage(_read_float(stream)), # 下部上下
            'tip_width': _format_float_to_percentage(_read_float(stream)),  # 先幅 (下巴尖端寬度)
            'tip_height': _format_float_to_percentage(_read_float(stream)), # 先上下 (下巴尖端上下)
            'tip_depth': _format_float_to_percentage(_read_float(stream)),  # 先前後 (下巴尖端前後)
        }

        # -- Cheeks 頰 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Cheeks' data.")
        face_data['cheeks'] = {
            'lower_height': _format_float_to_percentage(_read_float(stream)), # 下部上下
            'lower_depth': _format_float_to_percentage(_read_float(stream)),  # 下部前後
            'lower_width': _format_float_to_percentage(_read_float(stream)),  # 下部幅
            'upper_height': _format_float_to_percentage(_read_float(stream)), # 上部上下
            'upper_depth': _format_float_to_percentage(_read_float(stream)),  # 上部前後
            'upper_width': _format_float_to_percentage(_read_float(stream)),  # 上部幅
        }

        # -- Eyebrows 眉毛 1-- (眉弓骨/眉毛位置的調整)
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Brow' data.")
        face_data['eyebrows'] = {
            'height': _format_float_to_percentage(_read_float(stream)),     # 上下
            'horizontal_position': _format_float_to_percentage(_read_float(stream)), # 橫位置
            'angle_z': _format_float_to_percentage(_read_float(stream)),   # 角度Z軸
            'inner_shape': _format_float_to_percentage(_read_float(stream)), # 內側形狀
            'outer_shape': _format_float_to_percentage(_read_float(stream)), # 外側形狀
        } | temp_eyebrows
        

        # -- Eyes 目元 -- (眼周區域，包含眼裂、眼角等)
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Eyes' data.")
        face_data['eyes'] = {
            'height': _format_float_to_percentage(_read_float(stream)),         # 上下
            'horizontal_position': _format_float_to_percentage(_read_float(stream)), # 橫位置
            'depth': _format_float_to_percentage(_read_float(stream)),          # 前後
            'width': _format_float_to_percentage(_read_float(stream)),          # 橫幅
            'vertical_width': _format_float_to_percentage(_read_float(stream)), # 縱幅
            'angle_z': _format_float_to_percentage(_read_float(stream)),       # 角度Z軸
            'angle_y': _format_float_to_percentage(_read_float(stream)),       # 角度Y軸
            'inner_corner_h_pos': _format_float_to_percentage(_read_float(stream)), # 目頭左右位置
            'outer_corner_h_pos': _format_float_to_percentage(_read_float(stream)), # 目尻左右位置
            'inner_corner_v_pos': _format_float_to_percentage(_read_float(stream)), # 目頭上下位置
            'outer_corner_v_pos': _format_float_to_percentage(_read_float(stream)), # 目尻上下位置
            'eyelid_shape_1': _format_float_to_percentage(_read_float(stream)), # 眼瞼形狀1
            'eyelid_shape_2': _format_float_to_percentage(_read_float(stream)), # 眼瞼形狀2
        }

        # -- Eyeballs (Basic Settings) 眼球 (基本設定) --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Eyeballs (Basic Settings)' data.")
        face_data['eyeballs'] = {
            'pupil_v_adjustment': _format_float_to_percentage(_read_float(stream)), # 瞳的上下調整
            'pupil_width': _format_float_to_percentage(_read_float(stream)),    # 瞳的橫幅
            'pupil_vertical_width': _format_float_to_percentage(_read_float(stream)), # 瞳的縱幅
        } | temp_left_eye | temp_right_eye

        # -- Nose 鼻 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Nose' data.")
        face_data['nose'] = {
            'overall_height': _format_float_to_percentage(_read_float(stream)),    # 全体上下
            'overall_depth': _format_float_to_percentage(_read_float(stream)),     # 全体前後
            'overall_angle_x': _format_float_to_percentage(_read_float(stream)),   # 全体角度X軸
            'overall_width': _format_float_to_percentage(_read_float(stream)),     # 全体橫幅
            'bridge_height': _format_float_to_percentage(_read_float(stream)),     # 鼻筋高度
            'bridge_width': _format_float_to_percentage(_read_float(stream)),      # 鼻筋橫幅
            'bridge_shape': _format_float_to_percentage(_read_float(stream)),      # 鼻筋形狀
            'nostril_width': _format_float_to_percentage(_read_float(stream)),     # 小鼻橫幅
            'nostril_height': _format_float_to_percentage(_read_float(stream)),    # 小鼻上下
            'nostril_depth': _format_float_to_percentage(_read_float(stream)),     # 小鼻前後
            'nostril_angle_x': _format_float_to_percentage(_read_float(stream)),   # 小鼻角度X軸
            'nostril_angle_z': _format_float_to_percentage(_read_float(stream)),   # 小鼻角度Z軸
            'tip_height': _format_float_to_percentage(_read_float(stream)),        # 鼻尖高度
            'tip_angle_x': _format_float_to_percentage(_read_float(stream)),       # 鼻尖角度X軸
            'tip_size': _format_float_to_percentage(_read_float(stream)),          # 鼻尖大小
        }

        # -- Mouth 口 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Mouth' data.")
        face_data['mouth'] = {
            'height': _format_float_to_percentage(_read_float(stream)),      # 上下
            'width': _format_float_to_percentage(_read_float(stream)),       # 橫幅
            'vertical_width': _format_float_to_percentage(_read_float(stream)), # 縱幅
            'depth': _format_float_to_percentage(_read_float(stream)),       # 前後
            'upper_lip_shape': _format_float_to_percentage(_read_float(stream)), # 形狀上
            'lower_lip_shape': _format_float_to_percentage(_read_float(stream)), # 形狀下
            'corner_shape': _format_float_to_percentage(_read_float(stream)), # 形狀口角
        }

        # -- Ear 耳 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Ear' data.")
        face_data['ears'] = {
            'size': _format_float_to_percentage(_read_float(stream)),         # size
            'angle_y': _format_float_to_percentage(_read_float(stream)),      # 角度Y軸
            'angle_z': _format_float_to_percentage(_read_float(stream)),      # 角度Z軸
            'upper_shape': _format_float_to_percentage(_read_float(stream)),  # 上部形狀
            'lower_shape': _format_float_to_percentage(_read_float(stream)),  # 下部形狀
        }

        # -- Eyelashes 睫毛 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Eyelashes' data.")
        face_data['eyelashes'] = {
            'eyelash_id': _read_uint32(stream),     # 睫毛 ID
            '!extra_value': _read_uint32(stream),   # 2
            'eyelash_color': format_color_for_json(_read_color(stream)), # 睫毛顏色 (RGBA)
            '!shine_color': format_color_for_json(_read_color(stream)), # 睫毛光澤顏色 (RGBA) (185, 188, 177, 255) ??? 這個值會一直跳來跳去..
            'shine_strength': _format_float_to_percentage(_read_float(stream)), # 光澤強度
            'shine_texture': _format_float_to_percentage(_read_float(stream)),  # 光澤質感
        }

        # -- Eyeshadow 眼影 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Eyeshadow' data.")
        face_data['makeup']['eyeshadow'] = {
            'eyeshadow_id': _read_uint32(stream),   # 眼影 ID
            'color': format_color_for_json(_read_color(stream)), # 眼影顏色 (RGBA, alpha 無效)
        }
        

        # -- Blush 腮紅 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Blush' data.")
        face_data['makeup']['blush'] = {
            'blush_id': _read_uint32(stream),       # 腮紅 ID
            'color': format_color_for_json(_read_color(stream)), # 腮紅顏色 (RGBA, alpha 無效)
        }

        # -- Lipstick 唇膏 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Lipstick' data.")
        face_data['makeup']['lipstick'] = {
            'lipstick_id': _read_uint32(stream),    # 唇膏 ID
            'color': format_color_for_json(_read_color(stream)), # 唇膏顏色 (RGBA, alpha 無效)
        }

        # -- Mole 痣 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Mole' data.")
        face_data['mole'] = {
            'mole_id': _read_uint32(stream),        # 痣 ID
            'color': format_color_for_json(_read_color(stream)), # 痣顏色 (RGBA, alpha 無效)
        }

        # -- Eyeballs (Highlight) 眼球 (高光) --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Eyeballs (Highlight)' data.")
        face_data['eyeballs'].update(
            {
                'highlight_id': _read_uint32(stream), # 高光 ID
                '!extra_value': _read_uint32(stream), # extra value 7 ?
            
                'highlight_color': format_color_for_json(_read_color(stream)), # 高光顏色 (RGBA)
                '!highlight_shine': format_color_for_json(_read_color(stream)) # 高光光澤?!
            }
        )
        
        face_data['!strength?'] = _format_float_to_percentage(_read_float(stream))
        face_data['!texture?'] = _format_float_to_percentage(_read_float(stream))
        
        
        # 接下來是 6 bytes ?
        # 0x00 0x00 0x80 0x3F 0x00 0x00 似乎是 1.0 ...
        #face_data['!float1'] = _read_float(stream)
        #face_data['!padding2'] = _read_bytes_as_hex(stream, 2)
        

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