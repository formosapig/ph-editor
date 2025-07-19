# ph-editor/serializers/body_serializer.py

import json
import struct  # 引入 struct，儘管直接使用 common_types 中的封裝函式可能不需要直接用到
from io import BytesIO

from utils.common_types import _parse_and_pack_float  # 新增導入這個函式
from utils.common_types import _pack_color, _pack_float, _pack_hex_to_bytes, _pack_int32


def serialize_body_data(body_data: dict, stream: BytesIO):
    """
    將 parse_body_data 生成的 body_data dict 序列化回 BytesIO 二進位資料。
    使用 _pack_* 系列函式來轉換並寫入。

    Args:
        body_data: 包含身體數據的字典，格式應與 parse_body_data 的輸出一致。
        debug_mode: 是否開啟除錯模式，印出詳細序列化過程。
    """
    current_pos = stream.tell()  # 獲取初始位置
    # print(f"    [偏移: {current_pos}] 開始序列化身體數據。")

    try:
        # --- Overall Skin 全體 肌 ---
        if "overall" in body_data:
            overall = body_data["overall"]
            stream.write(_pack_int32(overall.get("skin_id", 0)))
            stream.write(_pack_int32(overall.get("skin_extra", 5)))
            # 這裡的 scale, min_val, max_val 參數參照 body_parser.py 中 _read_and_format_to_value 的設定
            stream.write(
                _parse_and_pack_float(overall.get("hue", 0), min_val=-50, max_val=50)
            )
            stream.write(
                _parse_and_pack_float(overall.get("saturation", 0), scale=50)
            )  # 預設 min_val=0, max_val=100
            stream.write(
                _parse_and_pack_float(overall.get("value", 0), scale=50)
            )  # 預設 min_val=0, max_val=100
            stream.write(
                _parse_and_pack_float(overall.get("!alpha", 0))
            )  # 預設 scale=100, min_val=0, max_val=100
            stream.write(
                _parse_and_pack_float(overall.get("gloss_strength", 0), scale=250)
            )  # 預設 min_val=0, max_val=100
            stream.write(
                _parse_and_pack_float(overall.get("gloss_texture", 0), scale=125)
            )  # 預設 min_val=0, max_val=100
            # !extra_value2 是一個 hex 字串
            stream.write(
                _pack_hex_to_bytes(overall.get("!extra_value2", "00 00 00 00"), 4)
            )
            # flesh_strength
            stream.write(
                _parse_and_pack_float(overall.get("flesh_strength", 0))
            )  # 預設 scale=100, min_val=0, max_val=100

        # -- Pubic Hair 陰毛 --
        if "pubic_hair" in body_data:
            ph_data = body_data["pubic_hair"]
            stream.write(_pack_int32(ph_data.get("id", 0)))
            stream.write(_pack_int32(ph_data.get("extra", 4)))
            stream.write(_pack_color(ph_data.get("color", "(255, 255, 255, 255)")))
            stream.write(_parse_and_pack_float(ph_data.get("!strength", 0)))
            stream.write(_parse_and_pack_float(ph_data.get("!texture", 0)))

        # -- Tattoo 刺青 --
        if "tattoo" in body_data:
            tat_data = body_data["tattoo"]
            stream.write(_pack_int32(tat_data.get("id", 0)))
            stream.write(_pack_color(tat_data.get("color", "(255, 255, 255, 255)")))
            stream.write(
                _pack_hex_to_bytes(tat_data.get("!padding1", "00 00 00 00"), 4)
            )

        # --- Overall Height 全體 身高 ---
        # 這裡的整體資料結構讓 height 屬於 overall，但獨立出來寫入
        if "overall" in body_data:
            stream.write(_parse_and_pack_float(body_data["overall"].get("height", 0)))

        # -- Chest 胸 --
        if "breast" in body_data:
            breast_fields = [
                "size",
                "vertical_position",
                "horizontal_spread",
                "horizontal_position",
                "angle",
                "firmness",
                "areola_prominence",
                "nipple_thickness",
            ]
            for field in breast_fields:
                stream.write(_parse_and_pack_float(body_data["breast"].get(field, 0)))

        # --- Overall Head Size 全体 頭大小 ---
        # 這裡的整體資料結構讓 head_size 屬於 overall，但獨立出來寫入
        if "overall" in body_data:
            stream.write(
                _parse_and_pack_float(body_data["overall"].get("head_size", 0))
            )

        # -- Upper Body 上半身 --
        if "upper_body" in body_data:
            upper_body_fields = [
                "neck_width",
                "neck_thickness",
                "torso_shoulder_width",
                "torso_shoulder_thickness",
                "torso_upper_width",
                "torso_upper_thickness",
                "torso_lower_width",
                "torso_lower_thickness",
            ]
            for field in upper_body_fields:
                stream.write(
                    _parse_and_pack_float(body_data["upper_body"].get(field, 0))
                )

        # -- Lower Body 下半身 --
        if "lower_body" in body_data:
            lower_body_fields = [
                "waist_position",
                "waist_upper_width",
                "waist_upper_thickness",
                "waist_lower_width",
                "waist_lower_thickness",
                "hip_size",
                "hip_angle",
            ]
            for field in lower_body_fields:
                stream.write(
                    _parse_and_pack_float(body_data["lower_body"].get(field, 0))
                )

        # -- Legs 脚 --
        if "legs" in body_data:
            leg_fields = ["thigh_upper", "thigh_lower", "calf", "ankle"]
            for field in leg_fields:
                stream.write(_parse_and_pack_float(body_data["legs"].get(field, 0)))

        # -- Arms 腕 --
        if "arms" in body_data:
            arm_fields = ["shoulder", "upper_arm", "forearm"]
            for field in arm_fields:
                stream.write(_parse_and_pack_float(body_data["arms"].get(field, 0)))

        # -- Chest (Nipple Erectness) 胸 --
        if "breast" in body_data:  # 屬於 breast 的子項
            stream.write(
                _parse_and_pack_float(body_data["breast"].get("nipple_erectness", 0))
            )

        # -- Nipples 胸 乳首 --
        if "breast" in body_data and "nipples" in body_data["breast"]:
            nip_data = body_data["breast"]["nipples"]  # 使用 breast 下的 nipples
            stream.write(_pack_int32(nip_data.get("id", 0)))
            stream.write(_pack_int32(nip_data.get("extra", 5)))

            # 根據您的要求，這裡不再使用迴圈，而是明確列出每個欄位
            stream.write(
                _parse_and_pack_float(
                    nip_data.get("hue", 0), scale=100, min_val=-50, max_val=50
                )
            )
            stream.write(_parse_and_pack_float(nip_data.get("saturation", 0), scale=50))
            stream.write(_parse_and_pack_float(nip_data.get("value", 0), scale=50))
            stream.write(_parse_and_pack_float(nip_data.get("alpha", 0)))
            stream.write(
                _parse_and_pack_float(nip_data.get("gloss_strength", 0), scale=250)
            )
            stream.write(
                _parse_and_pack_float(nip_data.get("gloss_texture", 0), scale=125)
            )

        # -- Tan Lines 曬痕 --
        if "tan_lines" in body_data:
            tan_data = body_data["tan_lines"]
            stream.write(_pack_int32(tan_data.get("id", 0)))
            stream.write(
                _parse_and_pack_float(
                    tan_data.get("hue", 0), scale=100, min_val=-50, max_val=50
                )
            )
            stream.write(_parse_and_pack_float(tan_data.get("saturation", 0), scale=50))
            stream.write(_parse_and_pack_float(tan_data.get("value", 0), scale=50))
            stream.write(_parse_and_pack_float(tan_data.get("intensity", 0)))
            stream.write(
                _pack_hex_to_bytes(tan_data.get("!padding1", "00 00 00 00"), 4)
            )

        # -- Nails 爪 --
        if "nails" in body_data:
            nails_data = body_data["nails"]
            stream.write(
                _parse_and_pack_float(
                    nails_data.get("hue", 0), scale=100, min_val=-50, max_val=50
                )
            )
            stream.write(
                _parse_and_pack_float(nails_data.get("saturation", 0), scale=50)
            )
            stream.write(_parse_and_pack_float(nails_data.get("value", 0), scale=50))
            stream.write(_parse_and_pack_float(nails_data.get("alpha", 0)))
            stream.write(_parse_and_pack_float(nails_data.get("gloss_strength", 0)))
            stream.write(_parse_and_pack_float(nails_data.get("gloss_texture", 0)))
            stream.write(
                _pack_hex_to_bytes(nails_data.get("!padding1", "00 00 00 00"), 4)
            )

            # -- Nail Polish 爪 指甲油 --
            if "polish" in nails_data:  # 屬於 nails 的子項
                polish_data = nails_data["polish"]
                stream.write(
                    _pack_color(polish_data.get("color", "(255, 255, 255, 255)"))
                )
                stream.write(
                    _pack_color(polish_data.get("!shine", "(255, 255, 255, 255)"))
                )
                stream.write(
                    _parse_and_pack_float(polish_data.get("shine_strength", 0))
                )
                stream.write(_parse_and_pack_float(polish_data.get("shine_texture", 0)))

        # -- Chest (Areola Size) 胸 乳首 --
        # 這個值在 parser 中是單獨讀取，但在 body_data 中屬於 nipples
        if "breast" in body_data and "nipples" in body_data["breast"]:
            stream.write(
                _parse_and_pack_float(
                    body_data["breast"]["nipples"].get("areola_size", 0)
                )
            )

        # -- Chest (Softness & Weight) 胸 --
        if "breast" in body_data:
            stream.write(_parse_and_pack_float(body_data["breast"].get("softness", 0)))
            stream.write(_parse_and_pack_float(body_data["breast"].get("weight", 0)))

    except Exception as e:
        print(f"    [錯誤] 序列化身體資料時發生未知錯誤: {e}")
        raise
