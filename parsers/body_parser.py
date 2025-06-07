# your_character_project/parsers/body_parser.py

from io import BytesIO
from common_types import (
    _read_uint32, _read_int32, _read_float, _read_color, format_color_for_json, _read_bytes_as_hex
)
import json
from game_data.body_data import get_body_by_id

# UI 界面整理的格式，可以根據需要定義，這裡只是一個示例
ui_body_category = [
    'overall', 'breast', 'upper_body', 'lower_body',
    'arms', 'legs', 'nails', 'pubic_hair',
    'tan_lines', 'tattoo'
]

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

# 新增一個函式來將浮點數轉換為 0-100 的整數值，並處理縮放和限制
def _format_float_to_scaled_percentage(value: float, scale: float = 100, min_val: int = 0, max_val: int = 100, debug_mode: bool = False) -> int:
    """
    將浮點數轉換為指定範圍內的整數值，並處理縮放和限制。
    """
    scaled_value = round(value * scale)
    if debug_mode:
        if not (min_val <= scaled_value <= max_val):
            print(f"    [WARN] Value {value} scaled to {scaled_value} is out of range [{min_val}, {max_val}], clamped.")
    return max(min_val, min(max_val, scaled_value))


def parse_body_data(stream: BytesIO, debug_mode: bool = False) -> dict:
    """
    解析角色的身體數據。
    Args:
        stream: 包含角色二進位資料的 BytesIO 串流物件。
        debug_mode: 是否開啟除錯模式，印出詳細解析過程。
    Returns:
        一個字典，包含解析後的身體數據。
    """
    body_data = {key: {} for key in ui_body_category}

    if debug_mode:
        current_pos = stream.tell()
        print(f"  [Offset: {current_pos}] Starting to parse body data.")

    try:
        # 請注意：這裡假設 stream 已經在正確的起始位置。
        # 如果不是，您可能需要 stream.seek(0x034E)
        # 但在一個連續的解析流程中，通常會依序讀取。

        # 先讀 16 bytes 出來看看...
        #body_data['test'] = _read_bytes_as_hex(stream, 32)


        # -- Overall Skin 全體 肌 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Overall Skin' data.")
        skin_id = (_read_int32(stream), _read_int32(stream))
        temp_overall = {
            'skin_id': f"({skin_id[0]}, {skin_id[1]})", # 對照肌表
            '#skin_name': get_body_by_id('skin', skin_id),
            'flesh_strength': None,
            'hue': _format_float_to_scaled_percentage(_read_float(stream), scale=100, min_val=-50, max_val=50, debug_mode=debug_mode), # 色相
            'saturation': _format_float_to_scaled_percentage(_read_float(stream), scale=50, min_val=0, max_val=100, debug_mode=debug_mode), # 彩度
            'lightness': _format_float_to_scaled_percentage(_read_float(stream), scale=50, min_val=0, max_val=100, debug_mode=debug_mode), # 明度
            '!alpha': _format_float_to_percentage(_read_float(stream)), # 透明度 (無法設定)
            'gloss_strength': _format_float_to_scaled_percentage(_read_float(stream), scale=250, min_val=0, max_val=100, debug_mode=debug_mode), # 光澤強度
            'gloss_texture': _format_float_to_scaled_percentage(_read_float(stream), scale=125, min_val=0, max_val=100, debug_mode=debug_mode), # 光澤質感
            '!extra_value2': _read_bytes_as_hex(stream, 4), #extra value 2 = 0 ? 
            #'flesh_strength': _format_float_to_percentage(_read_float(stream)), # 肉感強度
        }
        temp_overall['flesh_strength'] = _format_float_to_percentage(_read_float(stream)) # 肉感強度

        # -- Pubic Hair 陰毛 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Pubic Hair' data.")
        pubic_hair_id = (_read_int32(stream), _read_int32(stream))
        body_data['pubic_hair'] = {
            'id': f"({pubic_hair_id[0]}, {pubic_hair_id[1]})", # 對照陰毛表
            '#name': get_body_by_id('pubic_hair', pubic_hair_id),
            'color': format_color_for_json(_read_color(stream)), # 陰毛顏色 (Alpha 可設定) - 這裡原註解寫睫毛顏色，應為陰毛顏色
            '!strength': _format_float_to_percentage(_read_float(stream)),
            '!texture': _format_float_to_percentage(_read_float(stream)),
        }

        # -- Tattoo 刺青 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Tattoo' data.")
        tattoo_id = _read_int32(stream)
        body_data['tattoo'] = {
            'id': tattoo_id, # 對照刺青表
            '#name': get_body_by_id('tattoo', tattoo_id),
            'color': format_color_for_json(_read_color(stream)), # 刺青顏色
            # 0x43 0x00 0x00 0x00 感覺是跟著 Tattoo 的
            '!padding1': _read_bytes_as_hex(stream, 4) # 從 0x018E 到 0x0192，中間有 4 個 bytes 的空位        
        }

        # -- Overall Height 全體 身高 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Overall Height' data.")
        body_data['overall'] = {
            'height': _format_float_to_percentage(_read_float(stream)), # 身高
        }

        # -- Chest 胸 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Chest' data.")
        body_data['breast'] = {
            'size': _format_float_to_percentage(_read_float(stream)), # 胸部大小
            'vertical_position': _format_float_to_percentage(_read_float(stream)), # 胸上下位置
            'horizontal_spread': _format_float_to_percentage(_read_float(stream)), # 胸部左右張開
            'horizontal_position': _format_float_to_percentage(_read_float(stream)), # 胸部左右位置
            'angle': _format_float_to_percentage(_read_float(stream)), # 胸部上下角度
            'firmness': _format_float_to_percentage(_read_float(stream)), # 胸部尖挺
            'areola_prominence': _format_float_to_percentage(_read_float(stream)), # 乳暈隆起
            'nipple_thickness': _format_float_to_percentage(_read_float(stream)), # 乳頭粗細
        }

        # -- Overall Head Size 全体 頭大小 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Overall Head Size' data.")
        body_data['overall'].update(
            {
                'head_size': _format_float_to_percentage(_read_float(stream)), # 頭大小
            } | temp_overall
        )

        # -- Upper Body 上半身 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Upper Body' data.")
        body_data['upper_body'] = {
            'neck_width': _format_float_to_percentage(_read_float(stream)), # 脖子寬度
            'neck_thickness': _format_float_to_percentage(_read_float(stream)), # 脖子厚度
            'torso_shoulder_width': _format_float_to_percentage(_read_float(stream)), # 軀幹肩部寬度
            'torso_shoulder_thickness': _format_float_to_percentage(_read_float(stream)), # 軀幹肩部厚度
            'torso_upper_width': _format_float_to_percentage(_read_float(stream)), # 軀幹上部寬度
            'torso_upper_thickness': _format_float_to_percentage(_read_float(stream)), # 軀幹上部厚度
            'torso_lower_width': _format_float_to_percentage(_read_float(stream)), # 軀幹下部寬度
            'torso_lower_thickness': _format_float_to_percentage(_read_float(stream)), # 軀幹下部厚度
        }

        # -- Lower Body 下半身 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Lower Body' data.")
        body_data['lower_body'] = {
            'waist_position': _format_float_to_percentage(_read_float(stream)), # 腰部位置
            'waist_upper_width': _format_float_to_percentage(_read_float(stream)), # 腰部以上寬度
            'waist_upper_thickness': _format_float_to_percentage(_read_float(stream)), # 腰部以上厚度
            'waist_lower_width': _format_float_to_percentage(_read_float(stream)), # 腰部以下寬度
            'waist_lower_thickness': _format_float_to_percentage(_read_float(stream)), # 腰部以下厚度
            'hip_size': _format_float_to_percentage(_read_float(stream)), # 臀部大小
            'hip_angle': _format_float_to_percentage(_read_float(stream)), # 臀部角度
        }

        # -- Legs 脚 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Legs' data.")
        body_data['legs'] = {
            'thigh_upper': _format_float_to_percentage(_read_float(stream)), # 大腿上部
            'thigh_lower': _format_float_to_percentage(_read_float(stream)), # 大腿下部
            'calf': _format_float_to_percentage(_read_float(stream)), # 小腿肚
            'ankle': _format_float_to_percentage(_read_float(stream)), # 腳踝
        }

        # -- Arms 腕 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Arms' data.")
        body_data['arms'] = {
            'shoulder': _format_float_to_percentage(_read_float(stream)), # 肩膀
            'upper_arm': _format_float_to_percentage(_read_float(stream)), # 上臂
            'forearm': _format_float_to_percentage(_read_float(stream)), # 前臂
        }

        # -- Chest (Nipple Erectness) 胸 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Chest (Nipple Erectness)' data.")
        body_data['breast']['nipple_erectness'] = _format_float_to_percentage(_read_float(stream)) # 乳頭挺立

        # -- Nipples 胸 乳首 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Nipples' data.")
        nipples_id = (_read_int32(stream), _read_int32(stream))
        nipples = {
            'id': f"({nipples_id[0]}, {nipples_id[1]})", # 對照乳頭表
            '#name': get_body_by_id('nipples', nipples_id),
            'areola_size': None, # 佔位
            'hue': _format_float_to_scaled_percentage(_read_float(stream), scale=100, min_val=-50, max_val=50, debug_mode=debug_mode), # 色相
            'saturation': _format_float_to_scaled_percentage(_read_float(stream), scale=50, min_val=0, max_val=100, debug_mode=debug_mode), # 彩度
            'lightness': _format_float_to_scaled_percentage(_read_float(stream), scale=50, min_val=0, max_val=100, debug_mode=debug_mode), # 明度
            'alpha': _format_float_to_percentage(_read_float(stream)), # 透明
            'gloss_strength': _format_float_to_scaled_percentage(_read_float(stream), scale=250, min_val=0, max_val=100, debug_mode=debug_mode), # 光澤強度
            'gloss_texture': _format_float_to_scaled_percentage(_read_float(stream), scale=125, min_val=0, max_val=100, debug_mode=debug_mode), # 光澤質感
        }

        # -- Tan Lines 曬痕 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Tan Lines' data.")
        tan_lines_id = _read_int32(stream)
        body_data['tan_lines'] = {
            'id': tan_lines_id, # 對照曬痕表
            '#name': get_body_by_id('tan_lines', tan_lines_id),
            'hue': _format_float_to_scaled_percentage(_read_float(stream), scale=100, min_val=-50, max_val=50, debug_mode=debug_mode), # 色相
            'saturation': _format_float_to_scaled_percentage(_read_float(stream), scale=50, min_val=0, max_val=100, debug_mode=debug_mode), # 彩度
            'value': _format_float_to_scaled_percentage(_read_float(stream), scale=50, min_val=0, max_val=100, debug_mode=debug_mode), # 明度
            'intensity': _format_float_to_percentage(_read_float(stream)), # 濃度
            # 0x43 0x00 0x00 0x00 感覺是跟著 Tan Lines 的
            '!padding1': _read_bytes_as_hex(stream, 4)
        }

        # -- Nails 爪 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Nails' data.")
        body_data['nails'] = {
            'hue': _format_float_to_scaled_percentage(_read_float(stream), scale=100, min_val=-50, max_val=50, debug_mode=debug_mode), # 色相
            'saturation': _format_float_to_scaled_percentage(_read_float(stream), scale=50, min_val=0, max_val=100, debug_mode=debug_mode), # 彩度
            'lightness': _format_float_to_scaled_percentage(_read_float(stream), scale=50, min_val=0, max_val=100, debug_mode=debug_mode), # 明度
            'alpha': _format_float_to_percentage(_read_float(stream)), # 透明度 (不可修改)
            'gloss_strength': _format_float_to_percentage(_read_float(stream)), # 光澤強度
            'gloss_texture': _format_float_to_percentage(_read_float(stream)), # 光澤質感
            # 0x02 0x00 0x00 0x00 感覺是跟著 nails 的
            '!padding1': _read_bytes_as_hex(stream, 4)
        }

        # -- Nail Polish 爪 指甲油 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Nail Polish' data.")
        body_data['nails']['polish'] = {
            'color': format_color_for_json(_read_color(stream)), # 指甲油顏色 (Alpha 可設定)
            '!shine': format_color_for_json(_read_color(stream)), # 指甲油顏色 (Alpha 可設定)
            'shine_strength': _format_float_to_percentage(_read_float(stream)), # 光澤強度
            'shine_texture': _format_float_to_percentage(_read_float(stream)), # 光澤質感
        }

        # -- Chest (Areola Size) 胸 乳首 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Chest (Areola Size)' data.")
        # 這個值其實是屬於 'nipples' 分類下的 'areola_size'
        nipples['areola_size'] = _format_float_to_percentage(_read_float(stream)) # 乳暈大小

        # -- Chest (Softness & Weight) 胸 --
        if debug_mode: print(f"    [Offset: {stream.tell()}] Parsing 'Chest (Softness & Weight)' data.")
        body_data['breast']['softness'] = _format_float_to_percentage(_read_float(stream)) # 胸部柔軟
        body_data['breast']['weight'] = _format_float_to_percentage(_read_float(stream)) # 胸部重量
        body_data['breast']['nipples'] = nipples

        # padding ?
        #body_data['end_mark'] = _read_bytes_as_hex(stream, 4)

    except EOFError as e:
        if debug_mode:
            print(f"    [ERROR] Stream ended prematurely when parsing body data: {e}")
        raise
    except Exception as e:
        if debug_mode:
            print(f"    [ERROR] Unknown error occurred when parsing body data: {e}")
        raise

    if debug_mode:
        print(f"  Body data parsing complete. Next read position: {stream.tell()}")
        try:
            json_output = json.dumps(body_data, indent=2, ensure_ascii=False)
            print("\n  --- Body Parser JSON Debug Output ---")
            print(json_output)
            print("  -----------------------------------\n")
        except TypeError as json_e:
            print(f"\n  [CRITICAL ERROR] Body parser returned data cannot be JSON serialized: {json_e}")
            problematic_types = []
            def find_unserializable_in_dict(d):
                for k, v in d.items():
                    if isinstance(v, (bytes, bytearray)):
                        problematic_types.append(f"Key '{k}': {type(v)}")
                    elif isinstance(v, dict):
                        find_unserializable_in_dict(v)
            find_unserializable_in_dict(body_data)
            print(f"  Unserializable data types: {problematic_types}")
            print("  -----------------------------------\n")

    return body_data