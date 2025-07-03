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

# --- Profile Map 資料結構 ---
# Key: profile_id
# Value: profile 資料物件，包含 name、birth、physical 等欄位
DEFAULT_PROFILE_TEMPLATE = {
    '!version': 1,          # profile 版本號
    '!id': 0,               # profile id, 0 為特殊佔用, 創建新角色用
    'name': '新角色',        # 在列表上直接顯示為新角色
    'cup': 'A-',            # 罩杯
    'birth': 1911,          # 出生年份
    'height': 166,          # 身高
    'desc' : '用來創建新角色的佔位角色',
}
profile_map: Dict[int, Dict[str, Any]] = {
    0: DEFAULT_PROFILE_TEMPLATE
}

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

def build_profile_map_from_characters():
    """
    掃描所有 characters_db，根據每個角色的 profile_id 建立 profile_map。
    包含 character_ids 反向映射。
    """
    global profile_map
    profile_map = {}  # 先清空

    with characters_db_lock:
        for character_id, entry in characters_db.items():
            character_data = entry.get_character_data()
            if not character_data:
                continue

            profile_id = character_data.get_value(["profile_id"])
            profile_data = character_data.get_value(["profile"])
            
            if not profile_id or not isinstance(profile_data, dict):
                continue  # 忽略沒有 profile 的角色

            # 若 profile_id 不存在於 map 中，初始化
            if profile_id not in profile_map:
                # 複製 profile_data 並加入 character_ids 陣列
                profile_map[profile_id] = {
                    "id": profile_id,
                    "name": profile_data.get("name", ""),
                    "birth": profile_data.get("birth", ""),
                    "physical": profile_data.get("physical", {}),
                    "description": profile_data.get("description", ""),
                    "character_ids": []
                }

            # 加入當前角色 id
            profile_map[profile_id]["character_ids"].append(character_id)
            
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

            # 將新的 CharacterFileEntry 存入或更新 characters_db
            characters_db[character_id] = character_file_entry_obj

            # 比較並更新全域 general 資料（如果角色版本較新）
            char_ver = character_file_entry_obj.general_version or -1
            global_data = get_global_general_data()
            global_ver = global_data.get("!version", -1)
            if char_ver > global_ver:
                general_data = character_data_obj.get_value(["story", "general"])
                update_global_general_data(general_data)
                
                
                
            
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
    # 建立 profile map...
    build_profile_map_from_characters()                    

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

            # 將新的 CharacterFileEntry 存入或更新 characters_db
            characters_db[character_id] = character_file_entry_obj

            # 比較並更新全域 general 資料（如果角色版本較新）
            char_ver = character_file_entry_obj.general_version or -1
            global_data = get_global_general_data()
            global_ver = global_data.get("!version", -1)
            if char_ver > global_ver:
                general_data = character_data_obj.get_value(["story", "general"])
                update_global_general_data(general_data)
                
            # 假設 profile_map: Dict[int, Dict[str, Any]]
            profile_id = character_file_entry_obj.profile_id
            profile_version = character_file_entry_obj.profile_version

            if profile_id is not None:
                new_profile_data = character_file_entry_obj.get_profile()

                if profile_id in profile_map:
                    current_version = profile_map[profile_id].get("!version", -1)
                    if isinstance(profile_version, int) and profile_version > current_version:
                        profile_map[profile_id] = new_profile_data  # 更新資料
                else:
                    profile_map[profile_id] = new_profile_data  # 新增資料
                    
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
        
def get_profile_map() -> Dict[str, Dict[str, Any]]:
    """
    回傳目前的 profile_map 副本。
    """
    return profile_map.copy()

def add_profile(updated_profile: Dict[str, Any]):
    global profile_map
    
    # 若且唯若傳進來的 !id 為 0
    if updated_profile.get('!id') == 0:
      # 找出目前最大的 id
      new_id = max(profile_map.keys()) + 1
      updated_profile['!id'] = new_id
      
      # 將 profile 加入到 profile_map
      profile_map[new_id] = updated_profile
    else:
         print(f"add_profile with wrong id: {updated_profile.get('!id')}")

def update_profile(profile_id: str, updated_profile: Dict[str, Any]):
    """
    更新指定 profile 的資料，同步到所有相關角色的 character_data。
    並設定角色的 save_flag 為 True。
    """
    with characters_db_lock:
        if profile_id not in profile_map:
            return

        # 更新 profile_map 本身
        updated_profile["id"] = profile_id  # 確保 id 一致
        updated_profile["character_ids"] = profile_map[profile_id]["character_ids"]
        profile_map[profile_id] = updated_profile

        # 同步到所有角色
        for character_id in profile_map[profile_id]["character_ids"]:
            entry = characters_db.get(character_id)
            if not entry:
                continue

            char_data = entry.get_character_data()
            if not char_data:
                continue

            char_data.set_value(["profile"], {
                "name": updated_profile.get("name", ""),
                "birth": updated_profile.get("birth", ""),
                "physical": updated_profile.get("physical", {}),
                "description": updated_profile.get("description", "")
            })

            entry.set_save_flag(True)
            
def get_profiles_by_name(name: str) -> List[Dict[str, Any]]:
    """
    根據名稱模糊搜尋 profile（區分大小寫）。
    """
    return [p for p in profile_map.values() if name in p["name"]]            