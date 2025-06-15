import random
from io import BytesIO

import pytest

from serializers.hair_serializer import serialize_hair_data
from parsers.hair_parser import parse_hair_data
from game_data.hair_data import HAIR_STYLES, ACCESSORY_MARK, END_MARK

def id_to_tuple(s):
    return tuple(map(int, s.strip("()").split(",")))

def format_for_test(item):
    """構建用於序列化測試的 part_data 結構"""
    base = {
        "id": f"({item['id'][0]}, {item['id'][1]})",
        "#name": item['name']['ja'],  # 或 zh 無所謂，只要 parser 不修改就行
        "color": "(128, 64, 32, 255)",
        "shine1_color": "(255, 255, 255, 255)",
        "shine1_effect": random.randint(0, 100),
        "shine2_color": "(64, 64, 64, 255)",
        "shine2_effect": random.randint(0, 100)
    }
    if item.get("accessory"):
        base["accessory_mark"] = ACCESSORY_MARK
        base["accessory"] = {
            "color": "(200, 100, 50, 255)",
            "shine_color": "(150, 150, 150, 255)",
            "shine_strength": random.randint(0, 100),
            "shine_texture": random.randint(0, 100)
        }
    else:
        base["end_mark"] = END_MARK
    return base
    
# 若資源許可，建議測試：至少 300 次 roundtrip
# 想高置信度（>99%）→ 接近 400~500 次
# 若只想快速 smoke test，可做 50～100 次    
@pytest.mark.parametrize("_", range(50))  # 可依需求調整測試次數
def test_random_hair_roundtrip(_):
    original = {}

    for part in ["back", "front", "side"]:
        items = HAIR_STYLES.get(part)
        assert items, f"No items in category {part}"
        selected = random.choice(items)
        original[f"{part}_hair"] = format_for_test(selected)

    # 序列化並回讀
    stream = BytesIO()
    serialize_hair_data(original, stream)
    stream.seek(0)
    parsed = parse_hair_data(stream)

    # 比對每個欄位
    for part in ["back", "front", "side"]:
        for key, val in original[f"{part}_hair"].items():
            parsed_val = parsed[f"{part}_hair"][key]
            if key == "id":
                assert id_to_tuple(parsed_val) == id_to_tuple(val), f"{part}.id mismatch"
            else:
                assert parsed_val == val, f"{part}.{key} mismatch"
