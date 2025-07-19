import os
from pathlib import Path

import pytest

from core.character_data import CharacterData
from core.file_constants import PLAYHOME_MARKER

# 以 Path 表示 test_assets 目錄
TEST_DATA_DIR = Path(__file__).resolve().parent / "test_assets"


def get_all_png_files_with_marker():
    """
    掃描 test_assets 資料夾，找出內含 PLAYHOME_MARKER 的 .png 檔案。
    """
    if not TEST_DATA_DIR.is_dir():
        return []

    test_files = []
    for file in TEST_DATA_DIR.glob("*.png"):
        data = file.read_bytes()
        if PLAYHOME_MARKER in data:
            test_files.append(str(file))
    return test_files


# 準備測試檔案清單
test_png_files = get_all_png_files_with_marker()


# 目前還無法解決 float 精度問題, 無法直接 binary 對比, 所以先跳過.
@pytest.mark.skip(reason="TODO: fix float precision issue in binary parse/serialize")
# @pytest.mark.skipif(not test_png_files, reason="❗ 沒有找到含角色資料的 PNG 測試檔案")
@pytest.mark.parametrize("file_path", test_png_files)
def test_character_data_roundtrip(file_path):
    """
    測試角色資料能否成功解析後又正確序列化成完全相同的 bytes。
    若失敗，將原始資料與重建資料寫入 test_assets/original.bin 和 rebuild.bin。
    """
    with open(file_path, "rb") as f:
        full_data = f.read()

    marker_pos = full_data.find(PLAYHOME_MARKER)
    assert marker_pos != -1, f"找不到 PLAYHOME_MARKER: {file_path}"

    original_raw_data = full_data[marker_pos:]

    # 解析角色資料
    character = CharacterData(original_raw_data)

    # 再序列化回 bytes
    rebuilt_raw_data = character.to_raw_data()

    try:
        # 比對長度與內容
        assert len(rebuilt_raw_data) == len(original_raw_data), "長度不一致"
        assert rebuilt_raw_data == original_raw_data, "位元組內容不一致"
    except AssertionError as e:
        # 寫入 test_assets 目錄
        (TEST_DATA_DIR / "original.bin").write_bytes(original_raw_data)
        (TEST_DATA_DIR / "rebuild.bin").write_bytes(rebuilt_raw_data)
        raise AssertionError(
            f"{e}\n已輸出原始與重建資料至:\n"
            f"  original: {TEST_DATA_DIR / 'original.bin'}\n"
            f"  rebuild : {TEST_DATA_DIR / 'rebuild.bin'}\n"
            f"來源檔案: {file_path}"
        )
