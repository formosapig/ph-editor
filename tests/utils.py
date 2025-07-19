# ph-editor\tests\utils.py

import random
import re

import pytest


def _random_color_str():
    """生成一個隨機的 RGBA 顏色字串 (R, G, B, A)"""
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    a = 255  # 通常 Alpha 值為 255
    return f"({r}, {g}, {b}, {a})"


def _random_hex_string(length_bytes):
    """生成指定位元組長度的隨機十六進制字串，用空格分隔每兩個字符"""
    return " ".join(
        f"{random.randint(0, 255):02x}" for _ in range(length_bytes)
    ).upper()


# ✅ 加入你的測試工具函式
def compare_dicts(d1, d2, path=""):
    for k in d1:
        if k not in d2:
            pytest.fail(f"Key '{path}{k}' missing in parsed data.")

        val1 = d1[k]
        val2 = d2[k]

        if k.startswith("#"):
            continue

        if type(val1) != type(val2):
            pytest.fail(
                f"Type mismatch at {path}{k}: {type(val1).__name__} != {type(val2).__name__}"
            )

        if k.lower().endswith("_id") or k.lower() == "id" or k == "extra":
            if not isinstance(val1, int):
                pytest.fail(f"Original value for {path}{k} is not int: {val1!r}")
            if not isinstance(val2, int):
                pytest.fail(f"Parsed value for {path}{k} is not int: {val2!r}")
            assert (
                val1 == val2
            ), f"Mismatch at {path}{k}: Original={val1}, Parsed={val2}"

        elif isinstance(val1, dict):
            compare_dicts(val1, val2, path=f"{path}{k}.")

        elif isinstance(val1, str) and re.fullmatch(
            r"\(\d{1,3}, \d{1,3}, \d{1,3}, \d{1,3}\)", val1
        ):
            try:
                rgba1 = tuple(map(int, val1.strip("()").split(", ")))
                rgba2 = tuple(map(int, val2.strip("()").split(", ")))
                assert (
                    rgba1 == rgba2
                ), f"Mismatch at {path}{k} (color): Original={val1}, Parsed={val2}"
            except Exception:
                pytest.fail(f"Invalid color format at {path}{k}: {val1!r} or {val2!r}")

        elif isinstance(val1, float):
            if abs(val1 - val2) > 1e-6:
                pytest.fail(
                    f"Mismatch at {path}{k} (float): Original={val1}, Parsed={val2}"
                )

        elif isinstance(val1, int):
            if val1 != val2:
                pytest.fail(f"Mismatch at {path}{k}: Original={val1}, Parsed={val2}")

        else:
            assert (
                val1 == val2
            ), f"Mismatch at {path}{k}: Original={val1!r}, Parsed={val2!r}"

    for k in d2:
        if k not in d1 and not k.startswith("#"):
            pytest.fail(f"Extra key '{path}{k}' in parsed data.")
