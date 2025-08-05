# ph-editor/core/shared_data.py
import copy
import json
import threading
import logging
from typing import Any, Dict, List, Optional, Set

# 假設這些是從其他模組引入的
from .character_data import CharacterData
from .character_file_entry import CharacterFileEntry

logger = logging.getLogger(__name__)
#logger.disabled = True

# 全域字典，儲存所有載入的角色檔案數據
# Key: FILE_ID, 角色檔案的 ID (通常是檔名，不含路徑)
# Value: CharacterFileEntry 物件
characters_db: Dict[str, CharacterFileEntry] = {}

# --- 同步鎖 for characters_db 和相關操作 ---
# 為了保護 characters_db 在多執行緒/協程環境下的讀取和寫入
# 特別是針對 characters_db 字典本身的修改、sync_flag 的檢查和設置
characters_db_lock = threading.RLock()

# ----- general -----
DEFAULT_GENERAL_TEMPLATE = {
    "!version": 1,
    "color_traits": [
        {"code": "#FF0000", "name": {"en": "Red", "zh": "紅"}, "trait": {"zh": "熱情"}},
        {
            "code": "#0000FF",
            "name": {"en": "Blue", "zh": "藍"},
            "trait": {"zh": "冷靜"},
        },
    ],
    "tag_styles": {
        "setting": {
            "name": {"zh": "設定"},
            "order": 1,
            "color": "#808080",
            "background": "#000000",
        },
        "occupation": {
            "name": {"zh": "身份"},
            "order": 2,
            "color": "#0000FF",
            "background": "#00AAAA",
        },
    },
    "tag_list": [
        {
            "id": 1,
            "type": "setting",
            "name": {"zh": "virgin"},
            "desc": {"zh": "virgin"},
            "snapshot": {"zh": "拍照"},
            "marks": {"zh": "特徵"},
            "clothing": {"zh": "穿著"},
        },
        {
            "id": 2,
            "type": "opccupation",
            "name": {"zh": "學生"},
            "desc": {"zh": "一名學生"},
            "snapshot": {"zh": "拍照"},
            "marks": {"zh": "特徵"},
            "clothing": {"zh": "穿著"},
        },
    ],
    # NOTE: 簡化版模板。
}

# 全域 general 資料快取
global_general_data: Optional[Dict[str, Any]] = None

# ----- profile -----
DEFAULT_PROFILE_TEMPLATE = {
    "!id": 0,  # profile id, 0 為特殊佔用, 創建新角色用
    "!version": 1,  # profile 版本號
    "name": "新角色",  # 在列表上直接顯示為新角色
    "about": "關於角色",
    # NOTE: 簡化版模板。
}

# key : profile_id
# value : dict (DEFAULT_PROFILE_TEMPLATE)
profile_map: Dict[int, Dict[str, Any]] = {0: DEFAULT_PROFILE_TEMPLATE}

# key : profile_id
# value : set of file_id 
profile_file_ids: Dict[int, Set[str]] = {}

# ----- scenario series -----
DEFAULT_SCENARIO_TEMPLATE = {
    "!id": 0,          # scenario id, 0 為特殊佔用, 創建新場景用, 場景上限為 50 個.
    "!version": 1,     # 預計版本號
    "title": "新場景",  # 場景名稱
    "year": 1911       # 場景發生的年份
    # NOTE: 簡化版模板。
}

# key : scenario_id
# value : dict (DEFAULT_SCENARIO_TEMPLATE)
scenario_map: Dict[int, Dict[str, Any]] = {0: DEFAULT_SCENARIO_TEMPLATE}

# key : scenario_id
# value : set of file_id
scenario_file_ids: Dict[int, Set[str]] = {}

# ----- backstage -----
DEFAULT_BACKSTAGE_TEMPLATE = {
    "!tag_id": 1,
    "tag": "設定-virgin",
    "!persona_code": "#FF0000",
    "persona": "熱情",
    "!shadow_code": "#FF0000",
    "shadow": "熱情",
    # NOTE: 簡化版模板，會讀取設定資料。
}


def _is_valid_general_data(data: Dict[str, Any]) -> bool:
    """
    基礎格式驗證：確認必要欄位存在且格式正確
    """
    return True
    required_keys = ["!version", "color_traits", "tag_styles", "tag_list"]
    for key in required_keys:
        if key not in data:
            logger.debug(f"key fail {key}")
            return False

    if not isinstance(data["!version"], int):
        logger.debug("version is not int")
        return False
    if not isinstance(data["color_traits"], list):
        logger.debug("color_traits is not list")
        return False
    if not isinstance(data["tag_styles"], dict):
        logger.debug("tag_styles is not dict")
        return False
    if not isinstance(data["tag_list"], list):
        logger.debug("tag_list is not list")
        return False
    return True


def sync_global_general_to_characters(global_data: Dict[str, Any], global_version: int):
    """
    同步全域 general 資料到所有角色檔案：
    - 若角色 general 版本低於 global_version，更新其 general 節點資料
    - 並將該角色的 sync_flag 設為 True，等待儲存
    """
    from core.shared_data import characters_db, characters_db_lock

    logger.debug("準備同步全域資料")
    with characters_db_lock:
        for file_id, entry in characters_db.items():
            logger.debug(f"同步 {file_id}")
            character_data = entry.get_character_data()
            if not character_data:
                continue

            character_general = character_data.get_value(["story", "general"])
            character_version = -1
            if isinstance(character_general, dict):
                character_version = character_general.get("!version", -1)
            logger.debug(f"{file_id} : {character_version} vs {global_version}")

            if character_version < global_version:
                # 更新角色 general 節點資料
                data = character_data.get_data()
                if "story" not in data:
                    data["story"] = {}

                data["story"]["general"] = global_data
                # 設定角色物件屬性方便存檔
                entry.general_version = global_version
                entry.set_sync_flag(True)


def update_global_general_data(
    new_data: Dict[str, Any], increment_version: bool = False
):
    """
    更新全域 general 資料快取。
    這個函數本身不執行持久化。

    Args:
        new_data (Dict[str, Any]): 新的 general 資料字典（前端可能沒帶 '!version'）。
        increment_version (bool): 是否要將版本號加一，預設為 False。
    """
    global global_general_data
    
    logger.debug("enter update_global_general_data")
    
    # 僅當資料不合法且不要求版本更新時才略過更新
    if not increment_version and not _is_valid_general_data(new_data):
        return
    # print(new_data)

    if increment_version:
        logger.debug("更新版本號")
        # 從舊資料讀取版本號，預設 -1 表示沒版本
        original_version = (
            global_general_data.get("!version", -1) if global_general_data else -1
        )
        if isinstance(original_version, int) and original_version >= 0:
            new_version = original_version + 1
        else:
            new_version = 1
        # 把版本號寫入 new_data 裡
        new_data["!version"] = new_version
        logger.debug(f"新版本號 : {new_version}")
        sync_global_general_to_characters(new_data, new_version)

    global_general_data = new_data
    
    # 再次確認全域資料
    #current_global_general_data = get_global_general_data()
    #current_global_version = current_global_general_data.get("!version", -1)
    #logger.debug(f"after update global general data : {current_global_version}")


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


def add_or_update_character_with_path(scan_path: str, file_id: str):
    """
    從 scan_path + file_id 載入角色資料，解析後存入 characters_db。
    若角色資料中的 general 版本高於全域 general 資料快取，則更新全域資料。
    """
    with characters_db_lock:
        try:
            # 嘗試透過 CharacterFileEntry 讀取檔案並解析
            character_file_entry_obj = CharacterFileEntry.load(scan_path, file_id)
            character_data_obj = character_file_entry_obj.character_data

            # 將新的 CharacterFileEntry 存入或更新 characters_db
            characters_db[file_id] = character_file_entry_obj

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
            file_id = character_file_entry_obj.file_id

            if profile_id is not None:
                new_profile_data = character_file_entry_obj.get_profile()

                if profile_id in profile_map:
                    current_version = profile_map[profile_id].get("!version", -1)
                    if (
                        isinstance(profile_version, int)
                        and profile_version > current_version
                    ):
                        profile_map[profile_id] = new_profile_data  # 更新資料
                else:
                    profile_map[profile_id] = new_profile_data  # 新增資料

                # ✅ 縮排到這層：無論是否有更新 profile_map 都會同步對應
                if profile_id not in profile_file_ids:
                    profile_file_ids[profile_id] = set()
                profile_file_ids[profile_id].add(file_id)

            # 假設 scenario_map: Dict[int, Dict[str, Any]]
            scenario_id = character_file_entry_obj.scenario_id
            scenario_version = character_file_entry_obj.scenario_version
            file_id = character_file_entry_obj.file_id

            if scenario_id is not None:
                new_scenario_data = character_file_entry_obj.get_scenario()

                if scenario_id in scenario_map:
                    current_version = scenario_map[scenario_id].get("!version", -1)
                    if (
                        isinstance(scenario_version, int)
                        and scenario_version > current_version
                    ):
                        scenario_map[scenario_id] = new_scenario_data  # 更新資料
                else:
                    scenario_map[scenario_id] = new_scenario_data  # 新增資料

                # ✅ 縮排到這層：無論是否有更新 scenario_map 都會同步對應
                if scenario_id not in scenario_file_ids:
                    scenario_file_ids[scenario_id] = set()
                scenario_file_ids[scenario_id].add(file_id)

        except Exception as e:
            # 若讀取或解析失敗，清理 characters_db 和對應映射
            logger.error(f"處理 FILE ID '{file_id}' 時發生例外：{e}")


def get_character_file_entry(file_id: str) -> Optional[CharacterFileEntry]:
    """
    從 characters_db 中獲取 CharacterFileEntry。
    讀取 characters_db 也應該在鎖定下進行。
    """
    with characters_db_lock:
        return characters_db.get(file_id)


def get_character_data(file_id: str) -> Optional[CharacterData]:
    entry = get_character_file_entry(file_id)
    return entry.get_character_data() if entry else None


def clear_characters_db():
    """
    清空 characters_db 數據庫和 character_file_map。
    此操作會修改共享數據，因此必須在鎖的保護下進行。
    """
    with characters_db_lock:
        characters_db.clear()
        profile_map.clear()
        profile_file_ids.clear()
        # 恢復 profile_map 的初始設定
        profile_map[0] = DEFAULT_PROFILE_TEMPLATE
        scenario_map.clear()
        scenario_file_ids.clear()
        # 恢復 scenario_map 的初始設定
        scenario_map[0] = DEFAULT_SCENARIO_TEMPLATE
        logger.debug("角色數據庫已全部清空。")


def is_data_changed_without_version(
    current_data: Dict[str, Any], updated_data: Dict[str, Any]
) -> bool:
    # 檢查 !id 是否一致，若不一致拋出嚴重錯誤
    current_id = current_data.get("!id")
    updated_id = updated_data.get("!id")
    if current_id != updated_id:
        raise ValueError(f"[ERROR] ID mismatch: current !id={current_id}, updated !id={updated_id}")

    # 去除 !version 欄位
    def strip_version(data: Dict[str, Any]) -> Dict[str, Any]:
        return {k: v for k, v in data.items() if k != "!version"}

    logger.debug(f"current: {strip_version(current_data)}")
    logger.debug(f"updated: {strip_version(updated_data)}")

    # 比較是否相同
    if strip_version(current_data) != strip_version(updated_data):
        return True

    # 無不同
    logger.warning(f"ID {current_id} not changed.")
    return False


def add_profile(file_id: str, updated_profile: Dict[str, Any]) -> bool:
    # 若跟預設 id 一模一樣,則不更新
    if not is_data_changed_without_version(profile_map[0], updated_profile):
        return False

    # 要更新時, 要改 id, 版號預設為 1
    if updated_profile.get("!id") == 0:
        new_id = max(profile_map.keys(), default=0) + 1
        updated_profile["!id"] = new_id

        profile_map[new_id] = updated_profile

        # ✅ 更新物件屬性
        character_file_entry_obj = get_character_file_entry(file_id)
        if character_file_entry_obj is None:
            print(
                f"[ERROR] file_id {file_id} 找不到對應的 CharacterFileEntry"
            )
            return
        character_file_entry_obj.profile_id = new_id
        character_file_entry_obj.profile_version = updated_profile.get("!version", 0)
        character_file_entry_obj.sync_flag = True

        # ✅ 更新 profile_file_ids
        file_id = character_file_entry_obj.file_id
        if new_id not in profile_file_ids:
            profile_file_ids[new_id] = set()
        profile_file_ids[new_id].add(file_id)

        # add profile success
        return True

    else:
        print(f"[add_profile] Invalid profile id: {updated_profile.get('!id')}")
        return False


def sync_profile_to_characters(profile_id: int, updated_profile: Dict[str, Any]):
    """
    將指定 profile_id 的更新，同步到所有相關角色的 character_data。
    更新角色的 profile_version、profile 資料，並將 sync_flag 設為 True。
    """

    if profile_id not in profile_file_ids:
        print(f"[WARN] profile_id {profile_id} 沒有對應任何角色，跳過同步")
        return

    file_ids = profile_file_ids[profile_id]

    print(f"[INFO] 將更新 profile_id {profile_id} 的資料至以下角色：")
    print(json.dumps(updated_profile, ensure_ascii=False, indent=2))

    updated_version = updated_profile.get("!version", 0)
    updated_character_ids = []

    for file_id in file_ids:
        if file_id not in characters_db:
            print(
                f"[ERROR] file_id {file_id} 在 characters_db 中找不到對應的 CharacterFileEntry，跳過"
            )
            continue

        character_entry = characters_db[file_id]

        current_version = getattr(character_entry, "profile_version", 0)
        if current_version >= updated_version:
            # 版本已是最新或更高，跳過
            continue

        # 更新 profile_version
        character_entry.profile_version = updated_version

        # 更新 character_data.parsed_data[story]['profile']
        # 假設 story 是固定的字串或已知，這裡假設 story 名稱叫 "story"
        story = "story"
        if story not in character_entry.character_data.parsed_data:
            character_entry.character_data.parsed_data[story] = {}

        # 完整複製 profile 資料
        character_entry.character_data.parsed_data[story][
            "profile"
        ] = updated_profile.copy()

        # 設定 sync_flag
        character_entry.sync_flag = True

        updated_character_ids.append(file_id)

    print(f"[INFO] 更新完成，以下角色的資料被修改了: {updated_character_ids}")


def update_profile(file_id: str, updated_profile: Dict[str, Any]) -> bool:
    """
    更新指定 character 的 profile，如果 profile_id 有改變，
    需調整 profile_file_ids 的對應關係。
    """
    updated_profile_id = updated_profile.get("!id")
    if updated_profile_id is None:
        print("[ERROR] updated_profile 中缺少 '!id'")
        return False

    with characters_db_lock:
        character_file_entry_obj = get_character_file_entry(file_id)
        if character_file_entry_obj is None:
            print(
                f"[ERROR] file_id {file_id} 找不到對應的 CharacterFileEntry"
            )
            return False

        current_profile_id = character_file_entry_obj.profile_id

        # CASE 1: 後端無 profile（第一次）
        if current_profile_id is None:
            print(
                f"[INFO] file_id {file_id} 尚未設定 profile，新增為 {updated_profile_id}"
            )
            character_file_entry_obj.profile_id = updated_profile_id
            character_file_entry_obj.profile_version = (
                1  # 預設為 1, 前端的 !version 不可信
            )
            character_file_entry_obj.sync_flag = True
            profile_file_ids.setdefault(updated_profile_id, set()).add(
                file_id
            )

        # CASE 2: profile ID 改變（B -> A）
        elif current_profile_id != updated_profile_id:
            print(
                f"[INFO] file_id {file_id} profile 變更：{current_profile_id} -> {updated_profile_id}"
            )

            # 移除舊的關聯
            if current_profile_id in profile_file_ids:
                profile_file_ids[current_profile_id].discard(file_id)

            # 加入新的關聯
            profile_file_ids.setdefault(updated_profile_id, set()).add(
                file_id
            )

            # 更新 character 的 profile_id
            character_file_entry_obj.profile_id = updated_profile_id
            character_file_entry_obj.profile_version = (
                1  # 預設為 1, 前端的 !version 不可信
            )
            character_file_entry_obj.sync_flag = True

        # 檢查 profile_file_ids 中是否有該 profile_id
        if updated_profile_id not in profile_file_ids:
            logger.debug(
                f"[ERROR] profile_file_ids 中找不到 profile_id: {updated_profile_id}"
            )
            return False

        # 檢查該 profile_id 下是否有該 file_id
        if file_id not in profile_file_ids[updated_profile_id]:
            logger.debug(
                f"[ERROR] profile_id {updated_profile_id} 中找不到 file_id: {file_id}\n"
                f"目前存在的 character_ids: {list(profile_file_ids[updated_profile_id])}"
            )
            return False

        # 取得當前後端 profile，如果沒有，表示新增
        current_profile = profile_map.get(updated_profile_id)

        profile_changed = True  # 預設為有改變

        if current_profile is not None:
            profile_changed = is_data_changed_without_version(current_profile, updated_profile)

            if not profile_changed:
                if current_profile_id != updated_profile_id:
                    # Case: None → A 或 B → A 且 profile 沒有變更
                    print(
                        f"[INFO] profile_id {updated_profile_id} 沒有變更（但角色切換），不進行同步"
                    )
                    return True
                else:
                    # Case: A → A 且沒變更
                    print(f"[WARNING] profile_id {updated_profile_id} 未變更")
                    return False

        # 更新 profile_map 並升級版本
        updated = updated_profile.copy()
        current_version = current_profile.get("!version", 0) if current_profile else 0
        updated["!version"] = current_version + 1
        profile_map[updated_profile_id] = updated

        # 設定角色的 profile_version
        character_file_entry_obj.profile_version = updated["!version"]

    # 執行同步邏輯（放 lock 外）
    sync_profile_to_characters(updated_profile_id, updated)

    return True


def get_profile(profile_id: int) -> Dict[str, Any]:
    profile = profile_map.get(profile_id)
    if profile is None:
        raise ValueError(f"shared_data.py -> profile_id {profile_id} 不存在")
    return profile


def get_profile_name(file_id: str) -> str:
    entry = get_character_file_entry(file_id)
    if not entry:
        raise ValueError(f"❌ 找不到角色檔案。 FILE ID = {file_id}")

    if entry.profile_id is None:
        return ""  # 沒綁定 profile 是正常的情況

    profile = get_profile(entry.profile_id)
    if not profile:
        raise ValueError(
            f"❌ 找不到 profile："
            f"PROFILE ID = {entry.profile_id}, FILE ID = {file_id}"
        )

    name = profile.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError(
            f"❌ profile['name'] 無效或為空："
            f"PROFILE ID = {entry.profile_id}, FILE ID = {file_id}"
        )

    return name.strip()


def add_scenario(file_id: str, updated_scenario: Dict[str, Any]) -> bool:
    # 若跟預設 id 一模一樣,則不更新
    if not is_data_changed_without_version(scenario_map[0], updated_scenario):
        logger.debug("預設模板不需要更新。")
        return False

    # 要更新時, 要改 id, 版號預設為 1
    if updated_scenario.get("!id") == 0:
        new_id = max(scenario_map.keys(), default = 0) + 1
        updated_scenario["!id"] = new_id

        scenario_map[new_id] = updated_scenario

        # ✅ 更新物件屬性
        character_file_entry_obj = get_character_file_entry(file_id)
        if character_file_entry_obj is None:
            logger.error(f"File ID {file_id} 找不到對應的 CharacterFileEntry")
            return
        character_file_entry_obj.scenario_id = new_id
        character_file_entry_obj.scenario_version = updated_scenario.get("!version", 0)
        character_file_entry_obj.sync_flag = True

        # ✅ 更新 scenario_file_ids
        file_id = character_file_entry_obj.file_id
        if new_id not in scenario_file_ids:
            scenario_file_ids[new_id] = set()
        scenario_file_ids[new_id].add(file_id)

        # add profile success
        return True

    else:
        logger.warning(f"不是新場景不能走新增流程 : {updated_scenario.get('!id')}")
        return False


def sync_scenario_to_characters(scenario_id: int, updated_scenario: Dict[str, Any]):
    if scenario_id not in scenario_file_ids:
        logger.warning(f"SCENARIO ID {scenario_id} 沒有對應任何檔案，跳過同步。")
        return

    file_ids = scenario_file_ids[scenario_id]

    logger.debug(f"SCENARIO ID {scenario_id} 更新資料：")
    logger.debug(json.dumps(updated_scenario, ensure_ascii=False, indent=2))

    updated_version = updated_scenario.get("!version", 0)
    updated_file_ids = []

    for file_id in file_ids:
        if file_id not in characters_db:
            logger.error(f"FILE ID {file_id} 在 characters_db 中找不到對應的資料，跳過。")
            continue

        character_entry = characters_db[file_id]

        current_version = character_entry.scenario_version
        if current_version >= updated_version:
            # 版本已是最新或更高，跳過
            continue

        # 更新 profile_version
        character_entry.scenario_version = updated_version

        # 檢查 parsed_data[story][scenario] 是否存在
        if ("story" not in character_entry.character_data.parsed_data or
            "scenario" not in character_entry.character_data.parsed_data["story"]):
            raise KeyError("在 character_data.parsed_data 中找不到 'story' 或 'story' 裡的 'scenario' 資料。")

        # 完整複製 profile 資料
        character_entry.character_data.parsed_data["story"][
            "scenario"
        ] = updated_scenario.copy()

        # 設定 sync_flag
        character_entry.sync_flag = True

        updated_file_ids.append(file_id)

    logger.debug(f"場景同步完成，以下檔案被修改了: {updated_file_ids}")
    

def update_scenario(file_id: str, updated_scenario: Dict[str, Any]) -> bool:
    updated_scenario_id = updated_scenario.get("!id")
    if updated_scenario_id is None:
        logger.error("updated_scenario 中缺少 '!id'")
        return False

    with characters_db_lock:
        character_file_entry_obj = get_character_file_entry(file_id)
        if character_file_entry_obj is None:
            logger.error(f"FILE ID {file_id} 找不到對應的 CharacterFileEntry")
            return False

        current_scenario_id = character_file_entry_obj.scenario_id

        # CASE 1: 後端無 scenario（第一次）
        if current_scenario_id is None:
            logger.debug(f"FILE ID {file_id} 尚未設定場景，新增為 {updated_scenario_id}")
            character_file_entry_obj.scenario_id = updated_scenario_id
            character_file_entry_obj.scenario_version = (
                1  # 預設為 1, 前端的 !version 不可信
            )
            character_file_entry_obj.sync_flag = True
            scenario_file_ids.setdefault(updated_scenario_id, set()).add(file_id)

        # CASE 2: SCENARIO ID 改變（B -> A）
        elif current_scenario_id != updated_scenario_id:
            logger.debug(
                f"FILE ID {file_id} scenario 變更："
                "{current_scenario_id} -> {updated_scenario_id}"
            )

            # 移除舊的關聯
            if current_scenario_id in scenario_file_ids:
                scenario_file_ids[current_scenario_id].discard(file_id)

            # 加入新的關聯
            scenario_file_ids.setdefault(updated_scenario_id, set()).add(
                file_id
            )

            # 更新 character 的 scenario data
            character_file_entry_obj.scenario_id = updated_scenario_id
            character_file_entry_obj.scenario_version = (
                1  # 預設為 1, 前端的 !version 不可信
            )
            character_file_entry_obj.sync_flag = True

        # 檢查 scenario_file_ids 中是否有該 profile_id
        if updated_scenario_id not in scenario_file_ids:
            logger.debug(
                f"[ERROR] scenario_file_ids 中找不到 profile_id: {updated_scenario_id}"
            )
            return False

        # 檢查該 profile_id 下是否有該 file_id
        if file_id not in scenario_file_ids[updated_scenario_id]:
            logger.debug(
                f"[ERROR] profile_id {updated_scenario_id} 中找不到 file_id: {file_id}\n"
                f"目前存在的 character_ids: {list(scenario_file_ids[updated_scenario_id])}"
            )
            return False

        # 取得當前後端 profile，如果沒有，表示新增
        current_scenario = scenario_map.get(updated_scenario_id)

        scenario_changed = True  # 預設為有改變

        if current_scenario is not None:
            scenario_changed = is_data_changed_without_version(current_scenario, updated_scenario)

            if not scenario_changed:
                if current_scenario_id != updated_scenario_id:
                    # Case: None → A 或 B → A 且 profile 沒有變更
                    print(
                        f"[INFO] profile_id {updated_scenario_id} 沒有變更（但角色切換），不進行同步"
                    )
                    return True
                else:
                    # Case: A → A 且沒變更
                    print(f"[WARNING] profile_id {updated_scenario_id} 未變更")
                    return False

        # 更新 scenario_map 並升級版本
        updated = updated_scenario.copy()
        current_version = current_scenario.get("!version", 0) if current_scenario else 0
        updated["!version"] = current_version + 1
        scenario_map[updated_scenario_id] = updated

        # 設定角色的 profile_version
        character_file_entry_obj.scenario_version = updated["!version"]

    # 執行同步邏輯（放 lock 外）
    sync_scenario_to_characters(updated_scenario_id, updated)

    return True
    
    
def get_scenario(scenario_id: int) -> Dict[str, Any]:
    scenario = scenario_map.get(scenario_id)
    if scenario is None:
        raise ValueError(f"SCENARIO ID {scenario_id} 不存在。")
    return scenario
    
    
def get_scenario_title(file_id: str) -> str:
    entry = get_character_file_entry(file_id)
    if not entry:
        raise ValueError(f"❌ 找不到角色檔案。 FILE ID = {file_id}")

    if entry.scenario_id is None:
        return ""  # 沒綁定 scenario 是正常的情況

    scenario = get_scenario(entry.scenario_id)
    if not scenario:
        raise ValueError(
            f"❌ 找不到 scenario："
            f"SCENARIO ID = {entry.scenario_id}, file id = {file_id}"
        )

    title = scenario.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError(
            f"❌ scenario['title'] 無效或為空："
            f"SCENARIO ID = {entry.scenario_id}, FILE ID = {file_id}"
        )

    return title.strip()
    
    
def process_tag_info(file_id: str) -> tuple[str, str]:
    tag_style = ""
    tag_name = ""

    entry = get_character_file_entry(file_id)
    if not entry:
        raise ValueError(f"❌ 找不到角色檔案 ：'{file_id}'。")

    tag_id = entry.tag_id

    if tag_id is None:
        return tag_style, tag_name

    all_tags_list = global_general_data.get('tag_list', [])

    # 遍歷列表尋找匹配的 tag_id
    found_tag_data = None
    for tag_item in all_tags_list:
        if isinstance(tag_item, dict) and tag_item.get('id') == tag_id:
            found_tag_data = tag_item
            break

    if not found_tag_data:
        raise ValueError(
            f"無法在全域標籤資料中找到 tag_id "
            f"'{tag_id}' (角色ID: '{file_id}') 的資訊。"
        )

    tag_style = found_tag_data.get('type', "")
    tag_name = found_tag_data.get('name', {}).get('zh', "")

    return tag_style, tag_name


def get_default_backstage() -> dict:
    general_data = get_global_general_data()

    backstage = copy.deepcopy(DEFAULT_BACKSTAGE_TEMPLATE)

    # 檢查 global_general_data 是否已載入
    if general_data is None:
        # 如果 global_general_data 為 None，可能需要返回一個基本模板或報錯
        # 這裡選擇返回基於 DEFAULT_SCENARIO_TEMPLATE 的空值，或根據需求處理
        print("警告: global_general_data 尚未初始化，返回空的預設情境模板。")
        return backstage

    # --- 填充 !tag_id 和 tag ---
    if general_data.get('tag_list'):
        first_tag = general_data['tag_list'][0]
        backstage['!tag_id'] = first_tag['id']

        tag_type = first_tag['type']
        tag_style_name_zh = ""
        # 安全地從 tag_styles 獲取名稱
        if tag_type in general_data.get('tag_styles', {}):
            tag_style_name_zh = general_data['tag_styles'][tag_type]['name']['zh']

        tag_name_zh = first_tag['name']['zh']
        backstage['tag'] = f"{tag_style_name_zh}-{tag_name_zh}"
    else:
        # 如果 tag_list 為空或不存在
        backstage['!tag_id'] = None
        backstage['tag'] = ""


    # --- 填充 !persona_code 和 persona ---
    if general_data.get('color_traits'):
        first_color_trait = general_data['color_traits'][0]
        backstage['!persona_code'] = first_color_trait['code']
        backstage['persona'] = first_color_trait['trait']['zh']
    else:
        backstage['!persona_code'] = ""
        backstage['persona'] = ""


    # --- 填充 !shadow_code 和 shadow ---
    if general_data.get('color_traits') and len(general_data['color_traits']) > 0:
        last_color_trait = general_data['color_traits'][-1] # 使用 -1 取得最後一項
        backstage['!shadow_code'] = last_color_trait['code']
        backstage['shadow'] = last_color_trait['trait']['zh']
    else:
        backstage['!shadow_code'] = ""
        backstage['shadow'] = ""

    return backstage


def dump_all_data() -> None:
    """
    將當前作用域中的 global_general_data, profile_map, scenario_map
    以格式化的 JSON 形式輸出到 debug log。
    """
    
    logger.debug("\n--- Dumping All Data for Debug ---")

    # 處理 global_general_data
    if global_general_data is not None:
        try:
            logger.debug(
                "\n"
                + "Global General Data:\n"
                + json.dumps(global_general_data, ensure_ascii=False, indent=2)
            )
        except TypeError as e:
            logger.error(f"Error dumping global_general_data: {e}")
    else:
        logger.debug("Global General Data: None")

    # 處理 profile_map
    if profile_map is not None:
        try:
            logger.debug(
                "\n"
                + "Profile Map:\n"
                + json.dumps(profile_map, ensure_ascii=False, indent=2)
            )
        except TypeError as e:
            logger.error(f"Error dumping profile_map: {e}")
    else:
        logger.debug("Profile Map: None") # 實際上 profile_map 通常不會是 None 因為有預設值

    # 處理 scenario_map
    if scenario_map is not None:
        try:
            logger.debug(
                "\n"
                + "Scenario Map:\n"
                + json.dumps(scenario_map, ensure_ascii=False, indent=2)
            )
        except TypeError as e:
            logger.error(f"Error dumping scenario_map: {e}")
    else:
        logger.debug("Scenario Map: None") # 實際上 scenario_map 通常不會是 None 因為有預設值

    logger.debug("\n--- Dump Complete ---")
    

def get_suggest_file_name(file_id: str) -> str:
    """
    根據角色、情境或標籤資料，生成一個建議的檔案名稱。
    
    Args:
        file_id (str): 檔案的唯一 ID。
        
    Returns:
        str: 包含 '.png' 副檔名的建議檔名。
    """
    # 1. 取得檔案條目並檢查其有效性
    file_entry = get_character_file_entry(file_id)
    if not file_entry:
        return "未知.png"

    # 2. 判斷是否有 profile ID
    if file_entry.profile_id is None:
        return "未知.png"
    
    # 3. 取得 Profile 資料並檢查其有效性
    profile_data = get_profile(file_entry.profile_id)
    if not profile_data:
        return "未知.png"
        
    # 4. 根據 file_entry.scenario_id 是否為 None 來分流處理
    if file_entry.scenario_id is None:
        # 4a. 如果沒有 Scenario，則嘗試使用 Tag 資料
        tag_type, tag_name = process_tag_info(file_id)
        
        if not tag_name:
            return "未知.png"
        
        profile_name = profile_data.get("name", "")
        suggested_name = f"{tag_name}{profile_name}.png"
        return suggested_name.strip()
        
    else:
        # 4b. 如果有 Scenario ID，則取得情境資料並組合檔名
        scenario_data = get_scenario(file_entry.scenario_id)
        
        # 再次檢查情境資料是否成功取得
        if not scenario_data:
            # 即使有 ID，如果資料本身不存在，也回到沒有情境的邏輯
            tag_type, tag_name = get_tag_info(file_id)
            if not tag_name:
                return "未知.png"
            
            profile_name = profile_data.get("name", "")
            suggested_name = f"{tag_name}{profile_name}.png"
            return suggested_name.strip()

        # 取得年份資料
        born_year = profile_data.get("born")
        scenario_year = scenario_data.get("year")
        
        age_str = ""
        if born_year and scenario_year and isinstance(born_year, (int, str)) and isinstance(scenario_year, (int, str)):
            try:
                age = int(scenario_year) - int(born_year)
                age_str = f"({age})"
            except (ValueError, TypeError):
                pass

        profile_name = profile_data.get("name", "")
        scenario_title = scenario_data.get("title", "")
        
        suggested_name = f"{profile_name}{age_str}【{scenario_title}】.png"
        
        if not profile_name and not scenario_title:
             return "未知.png"
        
        return suggested_name.strip()
