# ph-editor/core/shared_data.py
import copy
import json
import threading
import logging
from typing import Any, Dict, List, Optional, Set, Tuple

# 假設這些是從其他模組引入的
from .character_data import CharacterData
from .character_file_entry import CharacterFileEntry

'''from .story_data import get_global_general_data'''
from .extra_data_manager import ExtraDataManager

logger = logging.getLogger(__name__)
#logger.disabled = True

# 全域字典，儲存所有載入的角色檔案數據
# Key: FILE_ID, 角色檔案的 ID (通常是檔名，不含路徑)
# Value: CharacterFileEntry 物件
characters_db: Dict[str, CharacterFileEntry] = {}

_extra_data_manager: Optional[ExtraDataManager] = None

def initialize_extra_data():
    """
    初始化並載入所有額外數據（general, profile, scenario, extra），
    並在完成後將數據輸出到日誌。
    """
    global _extra_data_manager
    if _extra_data_manager is None:
        _extra_data_manager = ExtraDataManager()
        _extra_data_manager.initialize_data()
        #_extra_data_manager.dump_all_data()


def get_general_data() -> Dict[str, Any]:
    return _extra_data_manager.get_general_data()


def update_general_data(new_data: Dict[str, Any]):
    _extra_data_manager.update_general_data(new_data)


def get_profile_map() -> Dict[int, Dict[str, Any]]:
    return _extra_data_manager.get_profile_map()
    

def get_scenario_map() -> Dict[int, Dict[str, Any]]:
    return _extra_data_manager.get_scenario_map()


def get_default_backstage() -> dict:    
    return _extra_data_manager.get_default_backstage()
    

# ---- 其他的唷~~~ -----
def add_or_update_character_with_path(scan_path: str, file_id: str) -> Optional[CharacterFileEntry]:
    try:
        # 嘗試透過 CharacterFileEntry 讀取檔案並解析
        character_file_entry_obj = (
            CharacterFileEntry.load(scan_path, file_id, _extra_data_manager)
        )
            
        # 將新的 CharacterFileEntry 存入或更新 characters_db
        characters_db[file_id] = character_file_entry_obj

        #logger.debug(character_file_entry_obj)

        return character_file_entry_obj

    except Exception as e:
        # 若讀取或解析失敗，清理 characters_db 和對應映射
        logger.error(f"處理 FILE ID '{file_id}' 時發生例外：{e}")
        return None # 失敗時明確回傳 None


def get_character_file_entry(file_id: str) -> Optional[CharacterFileEntry]:
    return characters_db.get(file_id)


def get_character_data(file_id: str) -> Optional[CharacterData]:
    entry = get_character_file_entry(file_id)
    return entry.get_character_data() if entry else None


def update_character_data(file_id: str, main_key: str, sub_key: str, data: any):
    entry = get_character_file_entry(file_id)
    if not entry:
       raise KeyError(f"Character {file_id} not found")
    entry.update_character_data(main_key, sub_key, data)

def clear_characters_db():
    characters_db.clear()
    logger.info("角色數據庫已全部清空。")
    _extra_data_manager.reload()
    logger.info("額外資料已重讀。")


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


def process_profile_data(
    file_id: str, updated_profile: Dict[str, Any]
) -> Tuple[bool, Optional[int]]:
    profile_id = updated_profile.get("!id")
    success = False
    new_profile_id = None
        
    if profile_id == 0:
        success = _extra_data_manager.add_profile(updated_profile)
        new_profile_id = updated_profile.get("!id", None) if success else None
    else:
        success = _extra_data_manager.update_profile(updated_profile)
        # 更新時, 不參考前端的 !version , updated_profile 也不會更新 !version

    if success: # 成功時,才更新 character_file_entry 的資料...
        character_file_entry_obj = get_character_file_entry(file_id)
        if character_file_entry_obj is None:
            print(
                f"[ERROR] file_id {file_id} 找不到對應的 CharacterFileEntry"
            )
            return False, None
        updated_profile_id = updated_profile.get("!id")
        logger.debug(f"PROFILE_ID: ${updated_profile_id}")
        character_file_entry_obj.update_profile_id(updated_profile_id)
            
    return success, new_profile_id


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


def process_scenario_data(
    file_id: str, updated_scenario: Dict[str, Any]
) -> Tuple[bool, Optional[int]]:
    scenario_id = updated_scenario.get("!id")
    success = False
    new_scenario_id = None
        
    if scenario_id == 0:
        success = _extra_data_manager.add_scenario(updated_scenario)
        new_scenario_id = updated_scenario.get("!id", None) if success else None
    else:
        success = _extra_data_manager.update_scenario(updated_scenario)
        # 更新時, 不參考前端的 !version , updated_profile 也不會更新 !version

    if success: # 成功時,才更新 character_file_entry 的資料...
        character_file_entry_obj = get_character_file_entry(file_id)
        if character_file_entry_obj is None:
            print(
                f"[ERROR] file_id {file_id} 找不到對應的 CharacterFileEntry"
            )
            return False, None
        updated_scenario_id = updated_scenario.get("!id")
        logger.debug(f"SCENARIO_ID: ${updated_scenario_id}")
        character_file_entry_obj.update_scenario_id(updated_scenario_id)
            
    return success, new_scenario_id

    
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
    
    
def update_backstage_data(
    file_id: str, updated_backstage: Dict[str, Any]
) -> bool:
    # 更新 backstage 資料永遠成功.
    _extra_data_manager.update_backstage(file_id, updated_backstage)
        
    character_file_entry_obj = get_character_file_entry(file_id)
    if character_file_entry_obj is None:
        raise KeyError(f"[ERROR] file_id {file_id} 找不到對應的 CharacterFileEntry")
    if '!tag_id' in updated_backstage:
        character_file_entry_obj.update_tag_id(updated_backstage['!tag_id'])
            
    return True
    
    
def process_tag_info(file_id: str) -> tuple[str, str]:
    tag_style = ""
    tag_name = ""

    entry = get_character_file_entry(file_id)
    if not entry:
        raise ValueError(f"❌ 找不到角色檔案 ：'{file_id}'。")

    tag_id = entry.tag_id

    if tag_id is None:
        return tag_style, tag_name

    general_data = _extra_data_manager.get_general_data()
    all_tags_list = general_data.get('tag_list', [])

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

def dump_profile_id():
    logger.debug(f"shared_data.py: profile_map 的 ID: {id(profile_map)}")    
