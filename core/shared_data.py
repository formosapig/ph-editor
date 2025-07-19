# ph-editor/core/shared_data.py
import json
import threading
import logging
from typing import Any, Dict, List, Optional, Set

# 假設這些是從其他模組引入的
from .character_data import CharacterData
from .character_file_entry import CharacterFileEntry

logger = logging.getLogger(__name__)

# 全域字典，儲存所有載入的角色檔案數據
# Key: 角色檔案的 ID (通常是檔名，不含路徑)
# Value: CharacterFileEntry 物件
characters_db: Dict[str, CharacterFileEntry] = {}

# 顯示 profile_id 到 character_id 的映射
# Key: profile_id (int)
# Value: 包含對應 character_id 的集合 (str)
profile_character_ids: Dict[str, Set[str]] = {}

# --- Profile Map 資料結構 ---
# Key: profile_id
# Value: profile 資料物件，包含 name、born、physical 等欄位
DEFAULT_PROFILE_TEMPLATE = {
    "!version": 1,  # profile 版本號
    "!id": 0,  # profile id, 0 為特殊佔用, 創建新角色用
    "name": "新角色",  # 在列表上直接顯示為新角色
    "about": "關於角色",
}

profile_map: Dict[int, Dict[str, Any]] = {0: DEFAULT_PROFILE_TEMPLATE}

# --- 同步鎖 for characters_db 和相關操作 ---
# 為了保護 characters_db 在多執行緒/協程環境下的讀取和寫入
# 特別是針對 characters_db 字典本身的修改、sync_flag 的檢查和設置
characters_db_lock = threading.RLock()

# --- 全域 general 資料預設值 ---
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
    "tag_type_setting": {
        "setting": {
            "name": {"zh": "設定"},
            "order": 1,
            "color": "#808080",
            "background": "#000000",
        },
        "opccupation": {
            "name": {"zh": "身份"},
            "order": 2,
            "color": "#0000FF",
            "background": "#00AAAA",
        },
    },
    "tag": [
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
    - 並將該角色的 sync_flag 設為 True，等待儲存
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
                character_version = character_general.get("!version", -1)
            # print(f"{character_id} : {character_version} vs {global_version}")

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

    # 僅當資料不合法且不要求版本更新時才略過更新
    if not increment_version and not _is_valid_general_data(new_data):
        return
    # print(new_data)

    if increment_version:
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
        sync_global_general_to_characters(new_data, new_version)

    global_general_data = new_data
    # current_global_general_data = get_global_general_data()
    # current_global_version = current_global_general_data.get("!version", -1)
    # print(f"after update global general data : {current_global_version}")


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


def add_or_update_character_with_path(scan_path: str, character_id: str):
    """
    從 scan_path + character_id 載入角色資料，解析後存入 characters_db。
    若角色資料中的 general 版本高於全域 general 資料快取，則更新全域資料。
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
            character_id = character_file_entry_obj.character_id

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
                if profile_id not in profile_character_ids:
                    profile_character_ids[profile_id] = set()
                profile_character_ids[profile_id].add(character_id)

        except Exception as e:
            # 若讀取或解析失敗，清理 characters_db 和對應映射
            print(f"[錯誤] 處理角色 '{character_id}' 時發生例外：{e}")


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


def clear_characters_db():
    """
    清空 characters_db 數據庫和 character_file_map。
    此操作會修改共享數據，因此必須在鎖的保護下進行。
    """
    with characters_db_lock:
        characters_db.clear()
        profile_character_ids.clear()
        # 移除 print 語句以符合之前移除除錯訊息的約定
        # print("角色數據庫和映射表已清空。")


def is_profile_changed(
    current_profile: Dict[str, Any], updated_profile: Dict[str, Any]
) -> bool:
    # 檢查 !id 是否一致，若不一致拋出嚴重錯誤
    current_id = current_profile.get("!id")
    updated_id = updated_profile.get("!id")
    if current_id != updated_id:
        error_msg = f"[ERROR] Profile ID mismatch: current !id={current_id}, updated !id={updated_id}"
        print(error_msg)
        raise ValueError(error_msg)

    # 去除 !version 欄位
    def strip_version(profile: Dict[str, Any]) -> Dict[str, Any]:
        return {k: v for k, v in profile.items() if k != "!version"}

    # 比較是否相同
    if strip_version(current_profile) != strip_version(updated_profile):
        # 有不同
        return True

    # 無不同
    print(f"[WARNING] Profile ID {current_id} not changed.")
    return False


def add_profile(character_id: str, updated_profile: Dict[str, Any]) -> bool:
    # 若跟預設 id 一模一樣,則不更新
    if not is_profile_changed(profile_map[0], updated_profile):
        return False

    # 要更新時, 要改 id, 版號預設為 1
    if updated_profile.get("!id") == 0:
        new_id = max(profile_map.keys(), default=0) + 1
        updated_profile["!id"] = new_id

        profile_map[new_id] = updated_profile

        # ✅ 更新物件屬性
        character_file_entry_obj = get_character_file_entry(character_id)
        if character_file_entry_obj is None:
            print(
                f"[ERROR] character_id {character_id} 找不到對應的 CharacterFileEntry"
            )
            return
        character_file_entry_obj.profile_id = new_id
        character_file_entry_obj.profile_version = updated_profile.get("!version", 0)
        character_file_entry_obj.sync_flag = True

        # ✅ 更新 profile_character_ids
        character_id = character_file_entry_obj.character_id
        if new_id not in profile_character_ids:
            profile_character_ids[new_id] = set()
        profile_character_ids[new_id].add(character_id)

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

    if profile_id not in profile_character_ids:
        print(f"[WARN] profile_id {profile_id} 沒有對應任何角色，跳過同步")
        return

    character_ids = profile_character_ids[profile_id]

    print(f"[INFO] 將更新 profile_id {profile_id} 的資料至以下角色：")
    print(json.dumps(updated_profile, ensure_ascii=False, indent=2))

    updated_version = updated_profile.get("!version", 0)
    updated_character_ids = []

    for character_id in character_ids:
        if character_id not in characters_db:
            print(
                f"[ERROR] character_id {character_id} 在 characters_db 中找不到對應的 CharacterFileEntry，跳過"
            )
            continue

        character_entry = characters_db[character_id]

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

        updated_character_ids.append(character_id)

    print(f"[INFO] 更新完成，以下角色的資料被修改了: {updated_character_ids}")


def update_profile(
    character_id: str, profile_id: int, updated_profile: Dict[str, Any]
) -> bool:
    """
    更新指定 profile 的資料，如果有變更，則同步到所有相關角色的 character_data，
    並設定角色的 sync_flag 為 True。
    """

    with characters_db_lock:
        character_file_entry_obj = get_character_file_entry(character_id)
        if character_file_entry_obj is None:
            print(
                f"[ERROR] character_id {character_id} 找不到對應的 CharacterFileEntry"
            )
            return False

        # 檢查 profile_id 是否存在
        if profile_id not in profile_map:
            print(f"[ERROR] profile_id {profile_id} 不存在於 profile_map")
            return False

        # 檢查 character_file_entry_obj.profile_id 與 profile_id 是否一致
        if character_file_entry_obj.profile_id != profile_id:
            print(
                f"[ERROR] character_file_entry_obj.profile_id ({character_file_entry_obj.profile_id}) 與傳入的 profile_id ({profile_id}) 不一致"
            )
            return False

        # 檢查 profile_character_ids 是否包含該 profile_id 且 character_id
        character_id = character_file_entry_obj.character_id
        if (
            profile_id not in profile_character_ids
            or character_id not in profile_character_ids[profile_id]
        ):
            print(
                f"[ERROR] profile_character_ids 中沒有對應的 profile_id {profile_id} 與 character_id {character_id}"
            )
            return False

        current_profile = profile_map[profile_id]

        if not is_profile_changed(current_profile, updated_profile):
            print(f"[WARNING] {profile_id} not changed.")
            return False

        # 更新 profile_map 並增加 !version
        updated = updated_profile.copy()
        current_version = current_profile.get("!version", 0)
        updated["!version"] = current_version + 1

        profile_map[profile_id] = updated

        # **注意：character_file_entry_obj.profile_id 不變**
        # 更新 character_file_entry_obj.profile_version
        character_file_entry_obj.profile_version = updated["!version"]

    # 執行同步邏輯（放在 lock 外）
    sync_profile_to_characters(profile_id, updated)

    return True


def update_profile1(character_id: str, updated_profile: Dict[str, Any]) -> bool:
    """
    更新指定 character 的 profile，如果 profile_id 有改變，
    需調整 profile_character_ids 的對應關係。
    """
    updated_profile_id = updated_profile.get("!id")
    if updated_profile_id is None:
        print("[ERROR] updated_profile 中缺少 '!id'")
        return False

    with characters_db_lock:
        character_file_entry_obj = get_character_file_entry(character_id)
        if character_file_entry_obj is None:
            print(
                f"[ERROR] character_id {character_id} 找不到對應的 CharacterFileEntry"
            )
            return False

        current_profile_id = character_file_entry_obj.profile_id

        # CASE 1: 後端無 profile（第一次）
        if current_profile_id is None:
            print(
                f"[INFO] character_id {character_id} 尚未設定 profile，新增為 {updated_profile_id}"
            )
            character_file_entry_obj.profile_id = updated_profile_id
            character_file_entry_obj.profile_version = (
                1  # 預設為 1, 前端的 !version 不可信
            )
            character_file_entry_obj.sync_flag = True
            profile_character_ids.setdefault(updated_profile_id, set()).add(
                character_id
            )

        # CASE 2: profile ID 改變（B -> A）
        elif current_profile_id != updated_profile_id:
            print(
                f"[INFO] character_id {character_id} profile 變更：{current_profile_id} -> {updated_profile_id}"
            )

            # 移除舊的關聯
            if current_profile_id in profile_character_ids:
                profile_character_ids[current_profile_id].discard(character_id)

            # 加入新的關聯
            profile_character_ids.setdefault(updated_profile_id, set()).add(
                character_id
            )

            # 更新 character 的 profile_id
            character_file_entry_obj.profile_id = updated_profile_id
            character_file_entry_obj.profile_version = (
                1  # 預設為 1, 前端的 !version 不可信
            )
            character_file_entry_obj.sync_flag = True

        # 檢查 profile_character_ids 中是否有該 profile_id
        if updated_profile_id not in profile_character_ids:
            logger.debug(
                f"[ERROR] profile_character_ids 中找不到 profile_id: {updated_profile_id}"
            )
            return False

        # 檢查該 profile_id 下是否有該 character_id
        if character_id not in profile_character_ids[updated_profile_id]:
            logger.debug(
                f"[ERROR] profile_id {updated_profile_id} 中找不到 character_id: {character_id}\n"
                f"目前存在的 character_ids: {list(profile_character_ids[updated_profile_id])}"
            )
            return False

        # 取得當前後端 profile，如果沒有，表示新增
        current_profile = profile_map.get(updated_profile_id)

        profile_changed = True  # 預設為有改變

        if current_profile is not None:
            profile_changed = is_profile_changed(current_profile, updated_profile)

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


def get_profile_name(character_id: str) -> str:
    entry = get_character_file_entry(character_id)
    if not entry:
        raise ValueError(f"❌ 找不到角色 entry：{character_id}")

    if entry.profile_id is None:
        return ""  # 沒綁定 profile 是正常的情況

    profile = get_profile(entry.profile_id)
    if not profile:
        raise ValueError(
            f"❌ 找不到 profile："
            f"profile_id = {entry.profile_id}, character_id = {character_id}"
        )

    name = profile.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError(
            f"❌ profile['name'] 無效或為空："
            f"profile_id = {entry.profile_id}, character_id = {character_id}"
        )

    return name.strip()


def get_profiles_by_name(name: str) -> List[Dict[str, Any]]:
    """
    根據名稱模糊搜尋 profile（區分大小寫）。
    """
    return [p for p in profile_map.values() if name in p["name"]]


def process_tag_info(character_id: str) -> tuple[str, str]:
    tag_style = ""
    tag_name = ""

    entry = get_character_file_entry(character_id)
    if not entry:
        raise ValueError(f"❌ 找不到角色 entry：'{character_id}'。")

    tag_id = entry.tag_id

    if tag_id is None:
        return tag_style, tag_name

    all_tags_list = global_general_data.get('tag', [])

    # 遍歷列表尋找匹配的 tag_id
    found_tag_data = None
    for tag_item in all_tags_list:
        if isinstance(tag_item, dict) and tag_item.get('id') == tag_id:
            found_tag_data = tag_item
            break

    if not found_tag_data:
        raise ValueError(
            f"無法在全域標籤資料中找到 tag_id "
            f"'{tag_id}' (角色ID: '{character_id}') 的資訊。"
        )

    tag_style = found_tag_data.get('type', "")
    tag_name = found_tag_data.get('name', {}).get('zh', "")

    return tag_style, tag_name
