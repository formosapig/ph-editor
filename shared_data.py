# your_flask_app/shared_data.py

from character_data import CharacterData # 引入 CharacterData 類別
# 你的 'PlayHome' 標記
from file_constants import PLAYHOME_MARKER

# 這個字典將用於儲存所有掃描到的角色數據。
# 鍵 (key) 將是檔案名 (不含 .png)。
# 值 (value) 將是 CharacterData 物件實例。
characters_db = {}


def add_or_update_character(character_id: str, raw_data_with_marker: bytes):
    """
    接收角色的 ID (檔案名不含副檔名) 和包含 'PlayHome' 標記的原始二進位數據。
    嘗試創建 CharacterData 物件並將其儲存到 characters_db 中。
    如果 key 值已存在，則會替換掉舊的 CharacterData 物件。

    Args:
        character_id: 角色的唯一 ID (例如檔案名，不含副檔名)。
        raw_data_with_marker: 從 PNG 檔案中提取的、包含 'PlayHome' 標記及其後續數據的原始位元組。
    """
    try:
        # 驗證 raw_data_with_marker 是否以 PlayHome 標記開頭
        if not raw_data_with_marker.startswith(PLAYHOME_MARKER):
            print(f"  [錯誤] 角色 '{character_id}' 的原始數據開頭不是預期的 '{PLAYHOME_MARKER.decode()}' 標記，跳過。")
            return

        # 創建 CharacterData 物件實例
        character_data_obj = CharacterData(raw_data_with_marker)

        # 將 CharacterData 物件實例儲存到全局字典中，如果存在則替換
        characters_db[character_id] = character_data_obj
        print(f"  成功載入/更新角色: '{character_id}' 到數據庫。")

    except Exception as e:
        print(f"  [錯誤] 處理角色 '{character_id}' 時發生錯誤: {e}")
        # 如果解析失敗，將其從 characters_db 中移除 (如果之前已添加)
        characters_db.pop(character_id, None)

def get_character_data(character_id: str) -> CharacterData | None:
    """
    從數據庫中獲取指定 ID 的 CharacterData 物件。

    Args:
        character_id: 角色的唯一 ID。

    Returns:
        CharacterData 物件實例，如果不存在則返回 None。
    """
    return characters_db.get(character_id)

def get_all_character_ids() -> list[str]:
    """
    返回數據庫中所有角色的 ID 列表。
    """
    return list(characters_db.keys())

def clear_characters_db():
    """
    清空 characters_db 數據庫。
    """
    characters_db.clear()
    print("角色數據庫已清空。")