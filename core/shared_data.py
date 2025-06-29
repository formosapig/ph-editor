import json
import os
import threading
from typing import Dict, Any, Optional, Set, List

# 假設這些是從其他模組引入的
from .character_data import CharacterData
from .character_file_entry import CharacterFileEntry
# UserConfigManager 雖然不再用於載入 general data，但如果應用其他地方仍需，可保留
from .user_config_manager import UserConfigManager 
from .file_constants import PLAYHOME_MARKER

# 全域字典，儲存所有載入的角色檔案數據
# Key: 角色檔案的 ID (通常是檔名，不含路徑)
# Value: CharacterFileEntry 物件
characters_db: Dict[str, CharacterFileEntry] = {}

# 顯示名稱到檔案 ID 的映射
# Key: 角色 display_name
# Value: 包含對應 character_id 的集合 (因為 display_name 可能重複)
character_file_map: Dict[str, Set[str]] = {}

# --- 同步鎖 for characters_db 和相關操作 ---
# 為了保護 characters_db 在多執行緒/協程環境下的讀取和寫入
# 特別是針對 characters_db 字典本身的修改、save_flag 的檢查和設置
characters_db_lock = threading.Lock()

# --- 全域 general 資料預設值 ---
DEFAULT_GENERAL_TEMPLATE = {
    '!version': 1,
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

# 全域 general 資料快取
global_general_data: Optional[Dict[str, Any]] = None

def _is_valid_general_data(data: Dict[str, Any]) -> bool:
    """
    基礎格式驗證：確認必要欄位存在且格式正確
    """
    required_keys = ["!version", "color_traits", "tag_type_setting", "tag"]
    for key in required_keys:
        if key not in data:
            print(f"key fail {key}")
            return False

    if not isinstance(data["!version"], int):
        print("version is not int")
        return False
    if not isinstance(data["color_traits"], list):
        print("color_traits is not list")
        return False
    if not isinstance(data["tag_type_setting"], dict):
        print("tag_type_setting is not dict")
        return False
    if not isinstance(data["tag"], list):
        print("tag is not list")
        return False
    return True

def sync_global_general_to_characters(global_data: Dict[str, Any], global_version: int):
    """
    同步全域 general 資料到所有角色檔案：
    - 若角色 general 版本低於 global_version，更新其 general 節點資料
    - 並將該角色的 save_flag 設為 True，等待儲存
    """
    from core.shared_data import characters_db, characters_db_lock

    with characters_db_lock:
        for character_id, entry in characters_db.items():
            character_data = entry.get_character_data()
            if not character_data:
                continue

            character_general = character_data.get_value(["story", "general"])
            character_version = -1
            if isinstance(character_general, dict):
                character_version = character_general.get('!version', -1)
            #print(f"{character_id} : {character_version} vs {global_version}")

            if character_version < global_version:
                # 更新角色 general 節點資料
                data = character_data.get_data()
                if "story" not in data:
                    data["story"] = {}

                data["story"]["general"] = global_data
                # 設定角色物件屬性方便存檔
                entry.general_version = global_version
                entry.set_save_flag(True)
                
def update_global_general_data(new_data: Dict[str, Any], increment_version: bool = False):
    """
    更新全域 general 資料快取。
    這個函數本身不執行持久化。

    Args:
        new_data (Dict[str, Any]): 新的 general 資料字典（前端可能沒帶 '!version'）。
        increment_version (bool): 是否要將版本號加一，預設為 False。
    """
    global global_general_data

    # 僅當資料不合法且不要求版本更新時才略過更新
    if not increment_version and not _is_valid_general_data(new_data):
        return
    #print(new_data)

    if increment_version:
        # 從舊資料讀取版本號，預設 -1 表示沒版本
        original_version = global_general_data.get('!version', -1) if global_general_data else -1
        if isinstance(original_version, int) and original_version >= 0:
            new_version = original_version + 1
        else:
            new_version = 1
        # 把版本號寫入 new_data 裡
        new_data['!version'] = new_version
        sync_global_general_to_characters(new_data, new_version)

    global_general_data = new_data
    #current_global_general_data = get_global_general_data()
    #current_global_version = current_global_general_data.get("!version", -1)
    #print(f"after update global general data : {current_global_version}")

def get_global_general_data() -> dict:
    """
    獲取當前的全域 general 資料。
    如果快取為空，則使用預設模板初始化。
    不執行本地持久化載入。
    """
    global global_general_data

    if global_general_data is None:
        global_general_data = DEFAULT_GENERAL_TEMPLATE

    return global_general_data

def _update_character_file_map(character_id: str, old_display_name: Optional[str], new_display_name: str):
    """
    更新 character_file_map。
    此函數應在持有 characters_db_lock 的情況下被呼叫。
    """
    if old_display_name and old_display_name != new_display_name:
        if old_display_name in character_file_map:
            character_file_map[old_display_name].discard(character_id)
            if not character_file_map[old_display_name]:
                del character_file_map[old_display_name]

    if new_display_name not in character_file_map:
        character_file_map[new_display_name] = set()
    character_file_map[new_display_name].add(character_id)

def add_or_update_character(character_id: str, raw_data_with_marker: bytes):
    """
    接收角色的 ID 和原始資料，解析後存入 characters_db。
    若角色資料中包含的 general 版本高於全域 general 資料快取，則更新全域資料。
    同時會更新 character_file_map。
    所有對 characters_db 的修改都應在這個鎖定區塊內進行。
    """
    # 對 characters_db 及其相關操作進行鎖定
    with characters_db_lock:
        try:
            if not raw_data_with_marker.startswith(PLAYHOME_MARKER):
                return

            old_display_name: Optional[str] = None
            if character_id in characters_db:
                old_display_name = characters_db[character_id].display_name

            character_data_obj = CharacterData(raw_data_with_marker)
            character_file_entry_obj = CharacterFileEntry(character_id, character_data_obj)

            general_from_char_data: Any = character_data_obj.get_value(["story", "general"])

            if not isinstance(general_from_char_data, dict) or "!version" not in general_from_char_data:
                character_file_entry_obj.general_version = 0
            else:
                character_file_entry_obj.general_version = general_from_char_data.get('!version', 0)
            
            # 將新的 CharacterFileEntry 存入或更新 characters_db
            characters_db[character_id] = character_file_entry_obj

            # 更新 character_file_map (也在鎖定區塊內)
            _update_character_file_map(character_id, old_display_name, character_file_entry_obj.display_name)

            # 進行全域 general 資料的版本比較和更新
            if isinstance(general_from_char_data, dict) and "!version" in general_from_char_data:
                current_global_general_data = get_global_general_data()
                current_global_version = current_global_general_data.get("!version", -1)
                character_general_version = general_from_char_data["!version"]

                if isinstance(character_general_version, int) and character_general_version > current_global_version:
                    update_global_general_data(general_from_char_data)
            
        except Exception:
            # 錯誤發生時，嘗試從 characters_db 和 character_file_map 中移除
            # 確保在鎖定區塊內執行這些清理操作
            if character_id in characters_db:
                removed_entry = characters_db.pop(character_id)
                if removed_entry.display_name and \
                   removed_entry.display_name in character_file_map and \
                   character_id in character_file_map[removed_entry.display_name]:
                    character_file_map[removed_entry.display_name].discard(character_id)
                    if not character_file_map[removed_entry.display_name]:
                        del character_file_map[removed_entry.display_name]

def add_or_update_character_with_path(character_id: str, scan_path: str):
    """
    從 scan_path + character_id 載入角色資料，解析後存入 characters_db。
    若角色資料中的 general 版本高於全域 general 資料快取，則更新全域資料。
    同時會更新 character_file_map。
    """
    with characters_db_lock:
        try:
            # 嘗試透過 CharacterFileEntry 讀取檔案並解析
            character_file_entry_obj = CharacterFileEntry.load(scan_path, character_id)
            character_data_obj = character_file_entry_obj.character_data

            old_display_name: Optional[str] = None
            if character_id in characters_db:
                old_display_name = characters_db[character_id].display_name

            # 嘗試讀取 general 版本資料
            general_from_char_data: Any = character_data_obj.get_value(["story", "general"])
            if not isinstance(general_from_char_data, dict) or "!version" not in general_from_char_data:
                character_file_entry_obj.general_version = 0
            else:
                character_file_entry_obj.general_version = general_from_char_data.get('!version', 0)

            # 更新 characters_db
            characters_db[character_id] = character_file_entry_obj

            # 更新角色名稱對映
            _update_character_file_map(character_id, old_display_name, character_file_entry_obj.display_name)

            # 若角色內 general 版本比全域還新，則更新全域 general
            if isinstance(general_from_char_data, dict) and "!version" in general_from_char_data:
                current_global_general_data = get_global_general_data()
                current_global_version = current_global_general_data.get("!version", -1)
                character_general_version = general_from_char_data["!version"]
                #print(f"{character_id} : {character_general_version} vs {current_global_version}")
                if isinstance(character_general_version, int) and character_general_version > current_global_version:
                    update_global_general_data(general_from_char_data)
                    #print(general_from_char_data)

        except Exception as e:
            # 若讀取或解析失敗，清理 characters_db 和對應映射
            print(f"[錯誤] 處理角色 '{character_id}' 時發生例外：{e}")

            if character_id in characters_db:
                removed_entry = characters_db.pop(character_id)
                if removed_entry.display_name and \
                   removed_entry.display_name in character_file_map and \
                   character_id in character_file_map[removed_entry.display_name]:
                    character_file_map[removed_entry.display_name].discard(character_id)
                    if not character_file_map[removed_entry.display_name]:
                        del character_file_map[removed_entry.display_name]
                        
def get_character_file_entry(character_id: str) -> Optional[CharacterFileEntry]:
    """
    從 characters_db 中獲取 CharacterFileEntry。
    讀取 characters_db 也應該在鎖定下進行。
    """
    with characters_db_lock:
        return characters_db.get(character_id)
        
def get_character_data(character_id: str) -> Optional[CharacterData]:
    """
    從數據庫中獲取指定 ID 的 CharacterData 物件。
    這是為了兼容舊的調用方式，建議直接使用 get_character_file_entry。

    Args:
        character_id: 角色的唯一 ID。

    Returns:
        CharacterData 物件實例，如果不存在則返回 None。
    """
    entry = get_character_file_entry(character_id)
    return entry.get_character_data() if entry else None

def get_all_character_ids() -> List[str]:
    """
    返回數據庫中所有角色的 ID 列表。
    此操作需要鎖保護，以確保讀取時的數據一致性。
    """
    with characters_db_lock:
        return list(characters_db.keys())

def get_character_ids_by_display_name(display_name: str) -> Set[str]:
    """
    根據角色顯示名稱，獲取所有相關的檔案 ID 集合。
    此操作需要鎖保護，以確保讀取時的數據一致性。

    Args:
        display_name: 角色在遊戲中顯示的名稱。

    Returns:
        一個包含相關檔案 ID 的集合，如果沒有找到則返回空集合。
    """
    with characters_db_lock:
        # 使用 .get() 並提供預設值，確保即使 display_name 不存在也不會出錯
        return character_file_map.get(display_name, set()).copy() # 回傳副本以避免外部直接修改內部集合

def clear_characters_db():
    """
    清空 characters_db 數據庫和 character_file_map。
    此操作會修改共享數據，因此必須在鎖的保護下進行。
    """
    with characters_db_lock:
        characters_db.clear()
        character_file_map.clear()
        # 移除 print 語句以符合之前移除除錯訊息的約定
        # print("角色數據庫和映射表已清空。") 