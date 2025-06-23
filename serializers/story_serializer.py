# ph-editor/serializers/story_serializer.py

from io import BytesIO
import zlib
import json

def serialize_story_data(story_data: dict, stream: BytesIO, debug_mode: bool = False):
    """
    將故事資料（story_data）序列化為 zlib 壓縮格式並寫入 BytesIO 串流。
    
    Args:
        story_data: 包含 general、character、scenario 三個主鍵的故事資料字典。
        stream: BytesIO 串流，用於寫入序列化資料。
        debug_mode: 是否啟用除錯輸出。
    """
    current_pos = stream.tell()
    print(f"    [偏移: {current_pos}] 開始序列化故事資料。")

    # 檢查是否為空內容（全部三個主鍵皆為空）
    if not any(story_data.get(key) for key in ["general", "character", "scenario"]):
        if debug_mode:
            print("    所有主鍵皆為空，略過寫入。")
        return  # 不寫入任何資料

    try:
        json_bytes = json.dumps(story_data, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        compressed_data = zlib.compress(json_bytes)
    except Exception as e:
        raise ValueError(f"    JSON 序列化或壓縮失敗: {e}")

    stream.write(compressed_data)

    if debug_mode:
        print(f"    故事資料序列化完成，寫入 {len(compressed_data)} 位元組。下一個寫入位置: {stream.tell()}")
