# ph-editor/parsers/story_parser.py

import json
import zlib
from io import BytesIO


def parse_story_data(stream: BytesIO, debug_mode: bool = False) -> dict:
    """
    解析其他零碎數據或處理無意義數據。
    若讀到資料尾端，回傳包含 general、character、scenario 的空字典。
    否則，讀取剩餘資料，使用 zlib 解壓縮，解析為 JSON 並轉為 dict。

    Args:
        stream: 包含角色二進位資料的 BytesIO 串流物件。
        debug_mode: 是否啟用除錯輸出。

    Returns:
        一個字典，包含 general、profile、scenario 三個主鍵。
    """
    current_pos = stream.tell()
    stream.seek(0, 2)  # 移到尾端以取得長度
    end_pos = stream.tell()
    stream.seek(current_pos)

    if current_pos >= end_pos:
        if debug_mode:
            print(f"    [偏移: {current_pos}] 已達資料尾端，回傳空白 story 結構。")
        return {"general": {}, "profile": {}, "scenario": {}}
        # ✅ 修改：當讀到資料尾端，回傳一個空的字典，明確表示沒有解析到任何 Story 數據。
        # return {}

    compressed_data = stream.read()
    if debug_mode:
        print(
            f"    [偏移: {current_pos}] 讀取 {len(compressed_data)} 位元組，開始解壓縮。"
        )

    try:
        decompressed_data = zlib.decompress(compressed_data)
        story_data = json.loads(decompressed_data.decode("utf-8"))
    except Exception as e:
        raise ValueError(f"    解壓縮或 JSON 解析失敗: {e}")

    # 確保三個主要 key 存在
    for key in ["general", "profile", "scenario"]:
        if key not in story_data:
            story_data[key] = {}

    if debug_mode:
        print(f"    解壓縮與解析完成，下一個讀取位置: {stream.tell()}")

    return story_data
