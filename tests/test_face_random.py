# ph-editor/tests/test_face_random.py

import random
from io import BytesIO

import pytest

from game_data.face_data import FACE_DETAILS
from parsers.face_parser import parse_face_data

# 導入序列化和解析函數
from serializers.face_serializer import serialize_face_data

# test utils
from tests.utils import _random_color_str, compare_dicts


def format_for_test(category_name, item):
    """
    構建用於序列化測試的 face_data 結構的一個部分。
    會填充隨機或預設的百分比、顏色值。
    """
    # 預設值，確保每個類別都有這些鍵，即使隨機選擇的 item 沒有它們
    # 這些是解析器預期會讀取的字段，不完全是 FACE_DETAILS 裡的鍵
    formatted_data = {}

    # 針對不同的 category_name 填充數據
    if category_name == "overall":
        formatted_data = {
            "contour_id": item["id"],
            "muscle_id": random.choice(FACE_DETAILS["muscle"])["id"],
            "wrinkle_id": random.choice(FACE_DETAILS["wrinkle"])["id"],
            "wrinkle_depth": random.randint(0, 100),
            "overall_width": random.randint(0, 100),
            "upper_part_depth": random.randint(0, 100),
            "upper_part_height": random.randint(0, 100),
            "lower_part_depth": random.randint(0, 100),
            "lower_part_width": random.randint(0, 100),
        }
    elif category_name == "chin":
        formatted_data = {
            "width": random.randint(0, 100),
            "height": random.randint(0, 100),
            "depth": random.randint(0, 100),
            "angle": random.randint(0, 100),
            "lower_height": random.randint(0, 100),
            "tip_width": random.randint(0, 100),
            "tip_height": random.randint(0, 100),
            "tip_depth": random.randint(0, 100),
        }
    elif category_name == "cheeks":
        formatted_data = {
            "lower_height": random.randint(0, 100),
            "lower_depth": random.randint(0, 100),
            "lower_width": random.randint(0, 100),
            "upper_height": random.randint(0, 100),
            "upper_depth": random.randint(0, 100),
            "upper_width": random.randint(0, 100),
        }
    elif category_name == "eyebrows":
        formatted_data = {
            "id": item["id"],  # eyebrows id
            "extra": 2,  # must be 2
            "color": _random_color_str(),
            "!shine": _random_color_str(),  # 預設值，或者從實際數據中獲取
            "strength": random.randint(0, 100),
            "texture": random.randint(0, 100),
            "height": random.randint(0, 100),
            "horizontal_position": random.randint(0, 100),
            "angle_z": random.randint(0, 100),
            "inner_shape": random.randint(0, 100),
            "outer_shape": random.randint(0, 100),
        }
    elif category_name == "eyes":
        formatted_data = {
            "height": random.randint(0, 100),
            "horizontal_position": random.randint(0, 100),
            "depth": random.randint(0, 100),
            "width": random.randint(0, 100),
            "vertical_width": random.randint(0, 100),
            "angle_z": random.randint(0, 100),
            "angle_y": random.randint(0, 100),
            "inner_corner_h_pos": random.randint(0, 100),
            "outer_corner_h_pos": random.randint(0, 100),
            "inner_corner_v_pos": random.randint(0, 100),
            "outer_corner_v_pos": random.randint(0, 100),
            "eyelid_shape_1": random.randint(0, 100),
            "eyelid_shape_2": random.randint(0, 100),
        }
    elif category_name == "eyeballs":
        formatted_data = {
            "pupil_v_adjustment": random.randint(0, 100),
            "pupil_width": random.randint(0, 100),
            "pupil_vertical_width": random.randint(0, 100),
            "left_eyeball": {
                "pupil_id": item["id"],
                "sclera_color": _random_color_str(),
                "pupil_color": _random_color_str(),
                "pupil_size": random.randint(0, 100),
                "pupil_brightness": random.randint(0, 100),
            },
            "right_eyeball": {
                "pupil_id": random.choice(FACE_DETAILS["eyeball"])[
                    "id"
                ],  # 另一隻眼睛也隨機選一個
                "sclera_color": _random_color_str(),
                "pupil_color": _random_color_str(),
                "pupil_size": random.randint(0, 100),
                "pupil_brightness": random.randint(0, 100),
            },
            "highlight_id": random.choice(FACE_DETAILS["highlight"])["id"],  # 高光 id
            "highlight_extra": 7,  # default is 7
            "highlight_color": _random_color_str(),
            "!highlight_shine": _random_color_str(),
            "!highlight_strength": random.randint(0, 100),
            "!highlight_texture": random.randint(0, 100),
        }
    elif category_name == "nose":
        formatted_data = {
            "overall_height": random.randint(0, 100),
            "overall_depth": random.randint(0, 100),
            "overall_angle_x": random.randint(0, 100),
            "overall_width": random.randint(0, 100),
            "bridge_height": random.randint(0, 100),
            "bridge_width": random.randint(0, 100),
            "bridge_shape": random.randint(0, 100),
            "nostril_width": random.randint(0, 100),
            "nostril_height": random.randint(0, 100),
            "nostril_depth": random.randint(0, 100),
            "nostril_angle_x": random.randint(0, 100),
            "nostril_angle_z": random.randint(0, 100),
            "tip_height": random.randint(0, 100),
            "tip_angle_x": random.randint(0, 100),
            "tip_size": random.randint(0, 100),
        }
    elif category_name == "mouth":
        formatted_data = {
            "height": random.randint(0, 100),
            "width": random.randint(0, 100),
            "vertical_width": random.randint(0, 100),
            "depth": random.randint(0, 100),
            "upper_lip_shape": random.randint(0, 100),
            "lower_lip_shape": random.randint(0, 100),
            "corner_shape": random.randint(0, 100),
        }
    elif category_name == "ears":
        formatted_data = {
            "size": random.randint(0, 100),
            "angle_y": random.randint(0, 100),
            "angle_z": random.randint(0, 100),
            "upper_shape": random.randint(0, 100),
            "lower_shape": random.randint(0, 100),
        }
    elif category_name == "eyelashes":
        formatted_data = {
            "id": item["id"],  # 睫毛的id
            "extra": 2,  # default is 2
            "color": _random_color_str(),
            "!shine": _random_color_str(),
            "strength": random.randint(0, 100),
            "texture": random.randint(0, 100),
        }
    elif category_name == "makeup":  # 彩妝類統一處理
        formatted_data = {
            "id": item["id"],
            "color": _random_color_str(),
        }
    elif category_name == "mole":
        formatted_data = {
            "id": item["id"],
            "color": _random_color_str(),
        }
    elif category_name == "tattoo":
        # 假設 tattoo 也有 id 和 color，就像 makeup 或 mole
        formatted_data = {
            "id": item["id"],
            "color": _random_color_str(),
            "!padding": "43 00 00 00",  # .join(random.choice('0123456789abcdef') for _ in range(8)) # 8個十六進制字符 = 4 bytes
        }
    else:
        # 如果有其他未處理的類別，可以在這裡添加日誌或錯誤處理
        print(f"Warning: Unhandled category for test formatting: {category_name}")
        return {}

    # 添加一個名稱，因為解析器可能會讀取它，儘管序列化時可能不會寫入
    if "id" in item and isinstance(item["id"], tuple):
        formatted_data["#name"] = item["name"]["ja"]  # 或 zh
    else:
        # 對於 int ID 的項目，解析器可能只返回 ID，所以 #name 可能不存在
        # 但如果解析器有邏輯將 ID 映射回名稱，則應包含
        pass

    return formatted_data


# 臉部所有會影響數據的類別，按照 parser 讀取順序大致排列
# 注意：'overall' 包含了 contour, muscle, wrinkle 和一些整體浮點參數
# 'eyebrows' 和 'eyelashes' 的 ID 是 (int, int)
# 'eyeballs' 則複雜，包含左右眼和高光
FACE_CATEGORIES_FOR_TEST = [
    "contour",  # 'overall' 數據中的一部分
    "eyebrows",
    "eyeball",  # 左右眼球選擇的類型
    "tattoo",
    # 整體參數 (float) - 這些在 serializer 中會被歸到 'overall' 下
    "chin",
    "cheeks",
    # 眉毛浮點參數 (float) - 這些在 serializer 中會被歸到 'eyebrows' 下
    "eyes",
    # 眼球浮點參數 (float) - 這些在 serializer 中會被歸到 'eyeballs' 下
    "nose",
    "mouth",
    "ears",
    # 睫毛浮點參數 (float) - 這些在 serializer 中會被歸到 'eyelashes' 下
    "eyeshadow",  # makeup 中的一部分
    "blush",  # makeup 中的一部分
    "lipstick",  # makeup 中的一部分
    "mole",
    # 高光參數 (id 和 float) - 這些在 serializer 中會被歸到 'eyeballs' 下
]

# 每一個類別都測到　95% 以上至少要 300 次


@pytest.mark.parametrize(
    "_", range(300)
)  # 可依需求調整測試次數，建議 50-100 次進行快速煙霧測試
def test_random_face_roundtrip(_):
    original_face_data = {}

    # 首先為 'overall' 結構化數據，因為它包含 contour, muscle, wrinkle
    selected_contour = random.choice(FACE_DETAILS.get("contour"))
    original_face_data["overall"] = format_for_test(
        "overall", selected_contour
    )  # 它會隨機選 muscle 和 wrinkle

    # 處理 'eyebrows'
    selected_eyebrows = random.choice(FACE_DETAILS.get("eyebrows"))
    original_face_data["eyebrows"] = format_for_test("eyebrows", selected_eyebrows)

    # 處理 'eyeballs'
    selected_eyeball = random.choice(
        FACE_DETAILS.get("eyeball")
    )  # 選擇一個眼球類型作為左眼預設
    original_face_data["eyeballs"] = format_for_test("eyeballs", selected_eyeball)

    # 處理 'tattoo'
    selected_tattoo = random.choice(FACE_DETAILS.get("tattoo"))
    original_face_data["tattoo"] = format_for_test("tattoo", selected_tattoo)

    # 處理其他獨立的類別 (浮點數和簡單 ID/Color)
    # 我們讓 format_for_test 為這些類別隨機生成數據，不需要傳入 specific item
    original_face_data["chin"] = format_for_test("chin", {})
    original_face_data["cheeks"] = format_for_test("cheeks", {})
    original_face_data["eyes"] = format_for_test("eyes", {})
    original_face_data["nose"] = format_for_test("nose", {})
    original_face_data["mouth"] = format_for_test("mouth", {})
    original_face_data["ears"] = format_for_test("ears", {})

    # 處理 'eyelashes'
    selected_eyelashes = random.choice(FACE_DETAILS.get("eyelashes"))
    original_face_data["eyelashes"] = format_for_test("eyelashes", selected_eyelashes)

    # 處理 'makeup' 子類別
    original_face_data["makeup"] = {
        "eyeshadow": format_for_test(
            "makeup", random.choice(FACE_DETAILS.get("eyeshadow"))
        ),
        "blush": format_for_test("makeup", random.choice(FACE_DETAILS.get("blush"))),
        "lipstick": format_for_test(
            "makeup", random.choice(FACE_DETAILS.get("lipstick"))
        ),
    }

    # 處理 'mole'
    selected_mole = random.choice(FACE_DETAILS.get("mole"))
    original_face_data["mole"] = format_for_test("mole", selected_mole)

    # --- 序列化並回讀 ---
    stream = BytesIO()
    serialize_face_data(original_face_data, stream)
    stream.seek(0)
    parsed_face_data = parse_face_data(stream)

    # --- 比對數據 ---
    # 因為結構是嵌套的，我們需要更詳細地比對
    # 這裡只比對解析器直接返回的頂層鍵
    # 由於 parser 和 serializer 的數據組織方式，需要分開比對
    # 例如，overall, eyebrows, eyeballs, makeup 的結構比較複雜

    print(f"\n--- Roundtrip Test {_+1} ---")
    print("Original data structure (simplified for comparison):")
    # 打印一些關鍵數據點以便於除錯
    print(f"  Overall Contour ID: {original_face_data['overall']['contour_id']}")
    print(f"  Eyebrows ID: {original_face_data['eyebrows']['id']}")
    print(
        f"  Left Eyeball ID: {original_face_data['eyeballs']['left_eyeball']['pupil_id']}"
    )
    print(f"  Tattoo ID: {original_face_data['tattoo']['id']}")

    print("\nParsed data structure (simplified for comparison):")
    print(f"  Overall Contour ID: {parsed_face_data['overall']['contour_id']}")
    print(f"  Eyebrows ID: {parsed_face_data['eyebrows']['id']}")
    print(
        f"  Left Eyeball ID: {parsed_face_data['eyeballs']['left_eyeball']['pupil_id']}"
    )
    print(f"  Tattoo ID: {parsed_face_data['tattoo']['id']}")

    # 開始遞歸比較
    compare_dicts(original_face_data, parsed_face_data)

    print(f"--- Roundtrip Test {_+1} Passed! ---")
