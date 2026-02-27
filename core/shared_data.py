# ph-editor/core/shared_data.py
import json
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

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
    """ 初始化並載入所有額外數據（general, profile, scenario, extra），並在完成後將數據輸出到日誌。 """
    global _extra_data_manager
    if _extra_data_manager is None:
        _extra_data_manager = ExtraDataManager()
        _extra_data_manager.initialize_data()
        #_extra_data_manager.dump_all_data()


def get_general_data() -> Dict[str, Any]:
    return _extra_data_manager.get_general_data()


def update_general_data(new_data: Dict[str, Any]):
    logger.debug("更新全域資料：")
    logger.debug(json.dumps(new_data, ensure_ascii=False, indent=2))
    _extra_data_manager.update_general_data(new_data)


def get_profile_map() -> Dict[int, Dict[str, Any]]:
    return _extra_data_manager.get_profile_map()
    

def get_scenario_map() -> Dict[int, Dict[str, Any]]:
    return _extra_data_manager.get_scenario_map()


def get_metadata_map() -> Dict[str, Dict[str, Any]]:
    return _extra_data_manager.get_metadata_map()


def get_default_backstage() -> dict:    
    return _extra_data_manager.get_default_backstage()


def get_wish_list() -> List[Dict[str, Any]]:
    return _extra_data_manager.get_wish_list()    


# ---- 其他的唷~~~ -----
def add_or_update_character_with_path(scan_path: str, file_id: str) -> Optional[CharacterFileEntry]:
    try:
        character_file_entry_obj = (
            CharacterFileEntry.load(scan_path, file_id, _extra_data_manager)
        )
        characters_db[character_file_entry_obj.sn] = character_file_entry_obj
        return character_file_entry_obj

    except Exception as e:
        logger.error(f"處理 FILE ID '{file_id}' 時發生例外：{e}")
        return None


def get_character_file_entry(sn: str) -> Optional[CharacterFileEntry]:
    return characters_db.get(sn)


def remove_character_file_entry(file_id: str):
    entry = characters_db.get(file_id)
    
    if not entry:
        logger.error(f"移除失敗:找不到 file_id 為 '{file_id}'")
        raise ValueError(f"找不到指定的角色資料: {file_id}")

    try:
        entry.remove_metadata()
        characters_db.pop(file_id, None)
        logger.info(f"成功將 {file_id} 從管理系統中移除。")
        
    except Exception as e:
        logger.error(f"移除 Entry {file_id} 時發生錯誤: {e}")
        raise RuntimeError(f"系統清理失敗: {str(e)}")


def get_character_data(sn: str) -> Optional[CharacterData]:
    entry = get_character_file_entry(sn)
    return entry.get_character_data() if entry else None


def update_character_data(sn: str, main_key: str, sub_key: str, data: any):
    entry = get_character_file_entry(sn)
    if not entry:
       raise KeyError(f"Character {sn} not found")
    entry.update_character_data(main_key, sub_key, data)


def clear_characters_db():
    characters_db.clear()
    logger.info("角色數據庫已全部清空。")
    _extra_data_manager.reload()
    logger.info("額外資料已重讀。")


def process_profile_data(
    sn: str, updated_profile: Dict[str, Any]
) -> Tuple[bool, Optional[int]]:
    profile_id = updated_profile.get("!id")
    success = False
    new_profile_id = None
        
    if profile_id == 0:
        success = _extra_data_manager.add_profile(updated_profile)
        new_profile_id = updated_profile.get("!id", None) if success else None
    else:
        success = _extra_data_manager.update_profile(updated_profile)

    if success: # 成功時,才更新 character_file_entry 的資料...
        character_file_entry_obj = get_character_file_entry(sn)
        if character_file_entry_obj is None:
            logger.error(f"SN:{sn} 找不到對應的 CharacterFileEntry")
            return False, None
        updated_profile_id = updated_profile.get("!id")
        logger.debug(f"PROFILE_ID: ${updated_profile_id}")
        character_file_entry_obj.update_profile_id(updated_profile_id)
            
    return success, new_profile_id


def process_scenario_data(
    sn: str, updated_scenario: Dict[str, Any]
) -> Tuple[bool, Optional[int]]:
    scenario_id = updated_scenario.get("!id")
    success = False
    new_scenario_id = None
    if scenario_id == 0:
        success = _extra_data_manager.add_scenario(updated_scenario)
        new_scenario_id = updated_scenario.get("!id", None) if success else None
    else:
        success = _extra_data_manager.update_scenario(updated_scenario)

    if success: # 成功時,才更新 character_file_entry 的資料...
        character_file_entry_obj = get_character_file_entry(sn)
        if character_file_entry_obj is None:
            logger.error(f"SN:{sn} 找不到對應的 CharacterFileEntry。")
            return False, None
        updated_scenario_id = updated_scenario.get("!id")
        logger.debug(f"SCENARIO_ID: ${updated_scenario_id}")
        character_file_entry_obj.update_scenario_id(updated_scenario_id)
            
    return success, new_scenario_id
  
    
def update_backstage_data(
    sn: str, updated_backstage: Dict[str, Any]
) -> bool:
    # 更新 backstage 資料永遠成功.
    _extra_data_manager.update_backstage(sn, updated_backstage)
        
    character_file_entry_obj = get_character_file_entry(sn)
    if character_file_entry_obj is None:
        raise KeyError(f"[ERROR] SN:{sn} 找不到對應的 CharacterFileEntry")
    if '!tag_id' in updated_backstage:
        character_file_entry_obj.update_tag_id(updated_backstage['!tag_id'])
            
    return True
    
    
def update_remark_data(sn: str, remark: str) -> bool:
    character_file_entry_obj = get_character_file_entry(sn)
    if character_file_entry_obj is None:
        raise KeyError(f"[ERROR] SN:{sn} 找不到對應的 CharacterFileEntry")
    character_file_entry_obj.update_remark(remark)
    return True    
    
def update_status_data(sn: str, status: str) -> bool:
    character_file_entry_obj = get_character_file_entry(sn)
    if character_file_entry_obj is None:
        raise KeyError(f"[ERROR] SM:{sn} 找不到對應的 CharacterFileEntry")
    character_file_entry_obj.update_status(status)
    return True    

def process_tag_info(sn: str) -> tuple[str, str]:
    tag_style = ""
    tag_name = ""

    entry = get_character_file_entry(sn)
    if not entry:
        raise ValueError(f"❌ 找不到角色檔案 ：'{sn}'。")

    tag_id = entry.tag_id
    if tag_id is None:
        return tag_style, tag_name

    general_data = _extra_data_manager.get_general_data()
    all_tags_list = general_data.get('tag_list', [])
    found_tag_data = None
    for tag_item in all_tags_list:
        if isinstance(tag_item, dict) and tag_item.get('id') == tag_id:
            found_tag_data = tag_item
            break
    if not found_tag_data:
        raise ValueError(
            f"無法在全域標籤資料中找到 tag_id "
            f"'{tag_id}' (角色SN: '{sn}') 的資訊。"
        )

    tag_style = found_tag_data.get('type', "")
    tag_name = found_tag_data.get('name', {}).get('zh', "")
    return tag_style, tag_name


def get_suggest_filename(file_id: str) -> str:
    """
    根據角色、情境或標籤資料，生成一個建議的檔案名稱。不包含副檔名。
    
    Args:
        file_id (str): 檔案的唯一 ID。
        
    Returns:
        str: 不包含副檔名的建議檔名。
    """
    # 0. fail file id
    failed_filename = "未知"
    
    # 1. 取得檔案條目並檢查其有效性
    file_entry = get_character_file_entry(file_id)
    if not file_entry:
        return failed_filename

    # 2. 判斷是否有 profile ID
    if file_entry.profile_id is None:
        return failed_filename
    
    # 3. 取得 Profile 資料並檢查其有效性
    profile_data = file_entry.get_profile()
    if not profile_data:
        return failed_filename
        
    # 4. 根據 file_entry.scenario_id 是否為 None 來分流處理
    if file_entry.scenario_id is None:
        # 4a. 如果沒有 Scenario，則嘗試使用 Tag 資料
        tag_type, tag_name = process_tag_info(file_id)
        
        logger.debug(f"process tag info : {tag_type}{tag_name}")
        
        if not tag_name:
            return failed_filename
        
        profile_name = profile_data.get("name", "")
        suggested_name = f"《{tag_name}》~{profile_name}"
        return suggested_name.strip()
        
    else:
        # 4b. 如果有 Scenario ID，則取得情境資料並組合檔名
        scenario_data = file_entry.get_scenario()
        
        # 再次檢查情境資料是否成功取得
        if not scenario_data:
            # 即使有 ID，如果資料本身不存在，也回到沒有情境的邏輯
            tag_type, tag_name = process_tag_info(file_id)
            if not tag_name:
                return failed_filename
            
            profile_name = profile_data.get("name", "")
            suggested_name = f"《{tag_name}》~{profile_name}"
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
        
        if not profile_name and not scenario_title:
             return failed_filename

        subtitle = file_entry.get_scenario_subtitle()
        subtitle_part = f"-{subtitle.strip()}" if subtitle and subtitle.strip() else ""
        suggested_name = f"{profile_name}{age_str}【{scenario_title}{subtitle_part}】"
        #suggested_name = f"{profile_name}{age_str}【{scenario_title}-{file_entry.get_scenario_subtitle()}】.png"
                
        return suggested_name.strip()


def find_another_file_id_by_scenario_id(
    scenario_id: int,
    sn_to_exclude: str
) -> Optional[str]:
    """
    掃描 characters_db，找出符合特定 scenario_id，
    但其 sn 不等於 sn_to_exclude 的第一個 sn。找不到則回傳 None。
    """
    if scenario_id is None or sn_to_exclude is None:
        return None
    
    for entry in characters_db.values():
        scenario_match = (entry.scenario_id == scenario_id)
        sn_mismatch = (entry.sn != sn_to_exclude)
        if scenario_match and sn_mismatch:
            return entry.file_id
            
    return None
    
def add_wish(data: Dict[str, Any]):
    wishes = get_wish_list()
    data['id'] = int(time.time() * 1000)
    data['date'] =time.strftime("%Y-%m-%d %H:%M")
    wishes.insert(0, data)
    _extra_data_manager.update_wish_list()    
    return data
    
def delete_wish(wish_id: int):
    wishes = get_wish_list()
    wishes[:] = [w for w in wishes if w['id'] != wish_id]
    _extra_data_manager.update_wish_list()
    


    