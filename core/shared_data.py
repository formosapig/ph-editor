# ph-editor/core/shared_data.py

from .character_data import CharacterData # 引入 CharacterData 類別
# 你的 'PlayHome' 標記
from .file_constants import PLAYHOME_MARKER
from .user_config_manager import UserConfigManager

# --- 全域 general 資料預設值 ---
DEFAULT_GENERAL_TEMPLATE = {
    'version': 1,
    'color_traits': [
        { 'code': '#FF0000', 'name': { 'en': 'Red', 'zh': '紅' }, 'trait': { 'zh': '熱情' } },
        { 'code': '#0000FF', 'name': { 'en': 'Blue', 'zh': '藍' }, 'trait': { 'zh': '冷靜' } }
    ],
    'tag_type_setting': {
        'setting': { 'index': 1, 'color': '#808080', 'background': '#000000' },
        'opccupation': { 'index': 2, 'color': '#0000FF', 'background': '#00AAAA' }
    },
    'tag': [
        { 'id': 1, 'type': 1, 'name': { 'zh': 'virgin' }, 'desc': { 'zh': 'virgin' }, 'snapshot': 'snapshot', 'restriction': 'restriction' },
        { 'id': 2, 'type': 2, 'name': { 'zh': '學生' }, 'desc': { 'zh': '一名學生' }, 'snapshot': 'snapshot', 'restriction': 'restriction' }
    ]
}

global_general_data = None

def _is_valid_general_data(data: dict) -> bool:
    """
    基礎格式驗證：確認必要欄位存在且格式正確
    """
    required_keys = ["version", "color_traits", "tag_type_setting", "tag"]
    for key in required_keys:
        if key not in data:
            print(f"[錯誤] 缺少必要欄位: '{key}'")
            return False

    if not isinstance(data["version"], int):
        print("[錯誤] 'version' 必須是整數")
        return False

    if not isinstance(data["color_traits"], list):
        print("[錯誤] 'color_traits' 必須是 list")
        return False

    if not isinstance(data["tag_type_setting"], dict):
        print("[錯誤] 'tag_type_setting' 必須是 dict")
        return False

    if not isinstance(data["tag"], list):
        print("[錯誤] 'tag' 必須是 list")
        return False

    # 更多細節檢查可於後續版本加入
    return True


def update_global_general_data(new_data: dict):
    global global_general_data

    if not isinstance(new_data, dict):
        print("[錯誤] 傳入資料不是 dict。")
        return

    if not _is_valid_general_data(new_data):
        print("[錯誤] 傳入的 general 資料格式不正確，未更新。")
        return

    global_general_data = new_data
    print(f"全域 general 資料已成功更新。版本: {new_data.get('version')}")

    # ✅ 同步儲存到本地設定檔
    try:
        UserConfigManager.save_general_data(new_data)
        print("已將 general 資料儲存至本地設定檔。")
    except Exception as e:
        print(f"[警告] 儲存本地 general 資料時出錯: {e}")


def get_global_general_data() -> dict:
    global global_general_data

    if global_general_data is None:
        persisted_data = UserConfigManager.load_general_data()
        if persisted_data and _is_valid_general_data(persisted_data):
            global_general_data = persisted_data
            print("已從本地設定載入 general 資料。")
        else:
            global_general_data = DEFAULT_GENERAL_TEMPLATE
            print("使用預設 general 資料模板。")

    return global_general_data
    
    
# 這個字典將用於儲存所有掃描到的角色數據。
# 鍵 (key) 將是檔案名 (不含 .png)。
# 值 (value) 將是 CharacterData 物件實例。
characters_db = {}

def add_or_update_character(character_id: str, raw_data_with_marker: bytes):
    """
    接收角色的 ID 和原始資料，解析後存入 characters_db。
    若包含 general 資料，會依據版本比較後決定是否更新全域 general 資料。
    """
    try:
        # 驗證 raw_data 是否以標記開頭
        if not raw_data_with_marker.startswith(PLAYHOME_MARKER):
            print(f"  [錯誤] 角色 '{character_id}' 的原始數據開頭不是預期的 '{PLAYHOME_MARKER.decode()}' 標記，跳過。")
            return

        # 建立角色資料物件
        character_data_obj = CharacterData(raw_data_with_marker)

        # 存入字典（覆蓋或新增）
        characters_db[character_id] = character_data_obj
        print(f"  成功載入/更新角色: '{character_id}' 到數據庫。")

        # 嘗試取得 general 區塊
        general = character_data_obj.get_value(["story", "general"])

        if isinstance(general, dict) and "version" in general:
            current_general = get_global_general_data()
            current_version = current_general.get("version", -1)
            new_version = general["version"]

            if isinstance(new_version, int) and new_version > current_version:
                print(f"  ✅ 更新全域 general 資料，來自角色 '{character_id}' (版本 {new_version} > {current_version})")
                update_global_general_data(general)  # ✅ 此函數內部現在會自動儲存
            else:
                print(f"  ⏭️ 角色 '{character_id}' 的 general 版本 {new_version} 未高於當前版本 {current_version}，跳過更新。")
        else:
            print(f"  ℹ️ 角色 '{character_id}' 沒有有效的 general 資料或缺少版本資訊。")

    except Exception as e:
        print(f"  [錯誤] 處理角色 '{character_id}' 時發生錯誤: {e}")
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