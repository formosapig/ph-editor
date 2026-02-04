# ph-editor/core/extra_data_manager.py
import os
import json
import logging
import copy
from typing import Any, Dict, List, Optional, Set

# 假設 UserConfigManager 已經存在，且負責提供檔案路徑
from core.user_config_manager import UserConfigManager
#from .shared_data import get_character_file_entry

logger = logging.getLogger(__name__)

# ----- 預設模板 -----
DEFAULT_GENERAL_TEMPLATE = {
    "color_traits": [
        {"code": "#FF0000", "name": {"en": "Red", "zh": "紅"}, "trait": {"zh": "熱情"}},
        {"code": "#0000FF", "name": {"en": "Blue", "zh": "藍"}, "trait": {"zh": "冷靜"}},
    ],
    "tag_styles": {
        "setting": {"name": {"zh": "設定"}, "order": 1, "color": "#808080", "background": "#000000"},
        "occupation": {"name": {"zh": "身份"}, "order": 2, "color": "#0000FF", "background": "#00AAAA"},
    },
    "tag_list": [
        {"id": 1, "type": "setting", "name": {"zh": "virgin"}, "desc": {"zh": "virgin"}},
        {"id": 2, "type": "occupation", "name": {"zh": "學生"}, "desc": {"zh": "一名學生"}},
    ],
}

DEFAULT_PROFILE_TEMPLATE = {
    "!id": 0,
    "!version": 1,
    "name": "新角色",
    "about": "關於角色",
}

DEFAULT_SCENARIO_TEMPLATE = {
    "!id": 0,
    "!version": 1,
    "title": "新場景",
    "year": 1911,
}

DEFAULT_BACKSTAGE_TEMPLATE = {
    "!tag_id": 1,
    "tag": "設定-virgin",
    "!persona_code": "#FF0000",
    "persona": "熱情",
    "!shadow_code": "#FF0000",
    "shadow": "熱情",
}

# --- 新增的 metadata 模板 ---
DEFAULT_METADATA_TEMPLATE = {
    "!profile_id": 0,
    "!scenario_id": 0,
    "backstage": DEFAULT_BACKSTAGE_TEMPLATE
}


class ExtraDataManager():
    def __init__(self):
        # 記憶體中的快取資料，將所有資料集中管理
        self._general_data: Optional[Dict[str, Any]] = None
        self._profile_map: Dict[int, Dict[str, Any]] = {}
        self._scenario_map: Dict[int, Dict[str, Any]] = {}
        self._metadata_map: Dict[str, Dict[str, Any]] = {}  # 每個 file_id 對應的獨有資料
        
    def _load_or_create(self, file_path_func, default_template, key_type=None):
        """
        輔助方法：嘗試從檔案載入資料，若失敗或檔案不存在，則使用預設模板。
        
        Args:
            file_path_func: 取得檔案路徑的函式。
            default_template: 檔案不存在或載入失敗時使用的預設模板。
            key_type: 鍵的類型，可以是 int 或 str。如果為 None，則不轉換。
            
        Returns:
            載入或創建的資料字典。
        """
        file_path = file_path_func()
        try:
            data = UserConfigManager.load_json_file(file_path)
            
            # 檢查是否為字典，如果不是，則資料格式不正確
            if not isinstance(data, dict):
                raise TypeError("載入的資料不是字典格式。")

            # 根據 key_type 進行鍵轉換
            if key_type == int:
                return {int(k): v for k, v in data.items()}
            elif key_type == str:
                return {str(k): v for k, v in data.items()}
            else:
                # key_type 為 None，不做任何轉換，直接返回
                return data
                
        except (FileNotFoundError, IOError, json.JSONDecodeError, TypeError, ValueError) as e:
            logger.info(f"載入檔案失敗 ({e})，使用預設模板。檔案路徑: {file_path}")
            # 返回預設模板的深層複製，避免共用同一份模板物件
            return copy.deepcopy(default_template)
            
    def initialize_data(self):
        """程式啟動時，載入所有資料。"""
        # 載入 general.json，key_type 為 None
        self._general_data = self._load_or_create(
            UserConfigManager.get_general_file_path, DEFAULT_GENERAL_TEMPLATE, key_type=None
        )
        
        # 載入 profile.json，key_type 為 int
        self._profile_map = self._load_or_create(
            UserConfigManager.get_profile_file_path, {0: DEFAULT_PROFILE_TEMPLATE}, key_type=int
        )
        
        # 載入 scenario.json，key_type 為 int
        self._scenario_map = self._load_or_create(
            UserConfigManager.get_scenario_file_path, {0: DEFAULT_SCENARIO_TEMPLATE}, key_type=int
        )
        
        # 載入 metadata.json，key_type 為 str, 這個 map 不創建預設值.
        self._metadata_map = self._load_or_create(
            UserConfigManager.get_metadata_file_path, {}, key_type=str
        )
        
    def reload(self):
        """清除並重新載入所有資料。"""
        logger.info("開始重新載入 ExtraDataManager 資料...")
        # 清除現有資料
        self._general_data = None
        self._profile_map = {}
        self._scenario_map = {}
        self._metadata_map = {}
        
        # 重新載入所有資料
        self.initialize_data()
        logger.info("ExtraDataManager 資料重新載入完成。")
        
    # 分別儲存各類資料的方法
    def _save_general_data(self):
        """儲存一般設定資料。"""
        if self._general_data:
            UserConfigManager.save_json_file(
                UserConfigManager.get_general_file_path(), self._general_data
            )
            
    def _save_profile_data(self):
        """儲存角色設定資料。"""
        if self._profile_map:
            UserConfigManager.save_json_file(
                UserConfigManager.get_profile_file_path(), self._profile_map
            )
            
    def _save_scenario_data(self):
        """儲存場景設定資料。"""
        if self._scenario_map:
            UserConfigManager.save_json_file(
                UserConfigManager.get_scenario_file_path(), self._scenario_map
            )
            
    def _save_metadata_data(self):
        """儲存後台資料。"""
        if self._metadata_map:
            UserConfigManager.save_json_file(
                UserConfigManager.get_metadata_file_path(), self._metadata_map
            )    
    
    # IDataAccessor
    def get_profile(self, profile_id: int) -> Dict[str, Any]:
        return self._profile_map.get(profile_id, {})

    def get_scenario(self, scenario_id: int) -> Dict[str, Any]:
        return self._scenario_map.get(scenario_id, {})

    def get_metadata(self, file_id: str) -> Dict[str, Any]:
        return self._metadata_map.get(file_id, {})
    
    # --- 對外提供的資料存取介面 ---
    def get_general_data(self) -> Dict[str, Any]:
        """獲取全域 general 資料。"""
        return self._general_data
        
    def get_profile_map(self) -> Dict[int, Dict[str, Any]]:
        """獲取所有 profile 資料。"""
        return self._profile_map
       
    def get_scenario_map(self) -> Dict[int, Dict[str, Any]]:
        """獲取所有 scenario 資料。"""
        return self._scenario_map
        
    def get_metadata_map(self) -> Dict[str, Dict[str, Any]]:
        return self._metadata_map    
            
    # --- 對外提供的更新介面 (會由 CharacterFileEntry 呼叫) ---
    
    def _is_data_changed_without_version(
        self, current_data: Dict[str, Any], updated_data: Dict[str, Any]
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
    
    def update_extra_data(self, file_id: str, new_extra_data: Dict[str, Any]):
        """更新特定檔案的獨有資料。"""
        self._backstage_map[file_id] = new_extra_data
        # TODO: 這裡可以選擇立即儲存或標記為需要儲存
        self.save_backstage_data()

    def update_general_data(self, new_data: Dict[str, Any]):
        """更新全域 general 資料。"""
        logger.debug("準備寫入全域資料了!!")
        logger.debug(json.dumps(self._general_data, ensure_ascii=False, indent=2))
        if new_data != self._general_data:
            self._general_data = new_data
            self._save_general_data()
            logger.debug("寫入全域資料：")
            logger.debug(json.dumps(new_data, ensure_ascii=False, indent=2))
            
    def add_profile(self, updated_profile: Dict[str, Any]) -> bool:
        ''' 新增一個 profile data, 並返回是否新增成功 '''
        # 1. 檢查跟 default 是不是一樣, 一樣返回 false.
        if not self._is_data_changed_without_version(
            DEFAULT_PROFILE_TEMPLATE,
            updated_profile
        ):
            return False
            
        # 2. 準備更新, 再檢查一次 profile_id 是 0 才做
        if updated_profile.get("!id") == 0:
            new_id = max(self._profile_map.keys(), default = 0) + 1
            updated_profile["!id"] = new_id # 重要!!這邊更新 profile_id 成新的.
            #copy_updated = copy.deepcopy(updated_profile) # 注意,做一個深層複製來維持封裝性.
            #self._profile_map[new_id] = copy_updated
            #self._save_profile_data() # 永遠即時儲存
            self._commit_profile(new_id, updated_profile)
            return True
        else:
            logger.error(f"無效的 PROFILE_ID: {updated_profile.get('!id')}")
            return False
        
    def update_profile(self, updated_profile: Dict[str, Any]) -> bool:
        """更新一個現有的 profile。"""
        updated_profile_id = updated_profile.get("!id")
        
        if updated_profile_id is None:
            logger.error(f"無效的 PROFILE_ID: {updated_profile_id}")
            return False

        # 找不到 profile , 嚴重錯誤
        current_profile = self._profile_map.get(updated_profile_id)
        if current_profile is None:
            raise KeyError(f"更新失敗：找不到 ID 為 '{updated_profile_id}' 的 profile。")
                
        # 資料都沒變, 但是外部需要成功, 來執行 character_file_entry <-> profile_id 的更新喔! 
        if not self._is_data_changed_without_version(current_profile, updated_profile):
            logger.info("資料沒有變動，無需更新。")
            return True 

        #updated = copy.deepcopy(updated_profile)
        #self._profile_map[updated_profile_id] = updated
        
        #self._save_profile_data()
        self._commit_profile(updated_profile_id, updated_profile) 
        return True
        
    def _commit_profile(self, profile_id: int, profile_data: Dict[str, Any]):
        """
        【私有核心：統一提交】
        負責排序、深拷貝、存入記憶體並觸發存檔。
        """
        # 如果你想做排序，就在這裡做，這樣 add 和 update 都能受益
        # ordered_data = self._sort_profile_keys(profile_data) 
        order = ["!id", "name", "!group_id", "group", "born", "job", "role", "height", "cup", "look", "sex", "about", "notes"]
        profile_data = {k: profile_data[k] for k in order if k in profile_data}
        
        # 執行深拷貝以維持封裝性
        copy_data = copy.deepcopy(profile_data)
        
        # 存入記憶體地圖
        self._profile_map[profile_id] = copy_data
        
        # 執行即時儲存
        self._save_profile_data()
        logger.info(f"Profile {profile_id} 提交成功並存檔。")
    
    def update_profile_id(self, file_id: str, profile_id: int):
        logger.debug(f"update PROFILE_ID: ${profile_id} to ${file_id}")
        # 要修改內容,直接內部讀取
        metadata = self._metadata_map.get(file_id, {})
        metadata['!profile_id'] = profile_id;
        self._metadata_map[file_id] = metadata
        self._save_metadata_data()
        
    def add_scenario(self, updated_scenario: Dict[str, Any]) -> bool:
        ''' 新增一個 scenario data, 並返回是否新增成功 '''
        # 1. 檢查跟 default 是不是一樣, 一樣返回 false.
        if not self._is_data_changed_without_version(
            DEFAULT_SCENARIO_TEMPLATE,
            updated_scenario
        ):
            return False
            
        # 2. 準備更新, 再檢查一次 scenario_id 是 0 才做
        if updated_scenario.get("!id") == 0:
            new_id = max(self._scenario_map.keys(), default = 0) + 1
            updated_scenario["!id"] = new_id # 重要!!這邊更新 profile_id 成新的.
            copy_updated = copy.deepcopy(updated_scenario) # 注意,做一個深層複製來維持封裝性.
            self._scenario_map[new_id] = copy_updated
            self._save_scenario_data() # 永遠即時儲存
            return True
        else:
            logger.error(f"無效的 SCENARIO_ID: {updated_scenario.get('!id')}")
            return False
        
    def update_scenario(self, updated_scenario: Dict[str, Any]) -> bool:
        """更新一個現有的 scenario。"""
        updated_scenario_id = updated_scenario.get("!id")
        
        if updated_scenario_id is None:
            logger.error(f"無效的 SCENARIO_ID: {updated_scenario_id}")
            return False

        # 找不到 scenario , 嚴重錯誤
        current_scenario = self._scenario_map.get(updated_scenario_id)
        if current_scenario is None:
            raise KeyError(f"更新失敗：找不到 ID 為 '{updated_scenario_id}' 的 scenario。")
                
        # 資料都沒變, 但是外部需要成功, 來執行 character_file_entry <-> scenario_id 的更新喔! 
        if not self._is_data_changed_without_version(current_scenario, updated_scenario):
            logger.info("資料沒有變動，無需更新。")
            return True 

        updated = copy.deepcopy(updated_scenario)
        self._scenario_map[updated_scenario_id] = updated
        
        self._save_scenario_data()

        return True
        
    def update_scenario_id(self, file_id: str, scenario_id: int):
        logger.debug(f"update SCENARIO_ID: ${scenario_id} to ${file_id}")
        # 要修改內容,直接內部讀取
        metadata = self._metadata_map.get(file_id, {})
        metadata['!scenario_id'] = scenario_id;
        self._metadata_map[file_id] = metadata
        self._save_metadata_data()
        
    def update_backstage(self, file_id: str, backstage_data: dict):
        metadata = self._metadata_map.get(file_id, {})
        metadata['backstage'] = backstage_data
        self._metadata_map[file_id] = metadata
        self._save_metadata_data()

    def update_remark(self, file_id: str, remark: str):
        metadata = self._metadata_map.get(file_id, {})
        metadata['!remark'] = remark
        self._metadata_map[file_id] = metadata
        self._save_metadata_data()

    def update_status(self, file_id: str, status: str):
        metadata = self._metadata_map.get(file_id, {})
        metadata['!status'] = status
        self._metadata_map[file_id] = metadata
        self._save_metadata_data()

    # --- 簡化版的 get_default_backstage 方法 ---
    def get_dafault_profile(self) -> Dict[str, Any]:
        return DEFAULT_PROFILE_TEMPLATE
        
    def get_default_scenario(self) -> Dict[str, Any]:
        return DEFAULT_SCENARIO_TEMPLATE    
    
    def get_default_backstage(self) -> dict:
        """根據 general 資料生成預設的 backstage 模板。"""
        backstage = copy.deepcopy(DEFAULT_BACKSTAGE_TEMPLATE)
        general_data = self.get_general_data()
        
        # 根據 general 資料填充預設值，邏輯與你提供的程式碼相同
        if general_data.get('tag_list'):
            first_tag = general_data['tag_list'][0]
            backstage['!tag_id'] = first_tag['id']
            tag_type = first_tag['type']
            tag_style_name_zh = general_data.get('tag_styles', {}).get(tag_type, {}).get('name', {}).get('zh', "")
            tag_name_zh = first_tag.get('name', {}).get('zh', "")
            backstage['tag'] = f"{tag_style_name_zh}-{tag_name_zh}"
        
        if general_data.get('color_traits'):
            first_color_trait = general_data['color_traits'][0]
            backstage['!persona_code'] = first_color_trait['code']
            backstage['persona'] = first_color_trait['trait']['zh']
            last_color_trait = general_data['color_traits'][-1]
            backstage['!shadow_code'] = last_color_trait['code']
            backstage['shadow'] = last_color_trait['trait']['zh']
            
        return backstage
        
    def dump_all_data(self) -> None:
        """
        將當前作用域中的 global_general_data, profile_map, scenario_map
        以格式化的 JSON 形式輸出到 debug log。
        """
        
        logger.debug("\n--- Dumping All Data for Debug ---")

        # 處理 global_general_data
        if self._general_data is not None:
            try:
                logger.debug(
                    "\n"
                    + "Global General Data:\n"
                    + json.dumps(self._general_data, ensure_ascii=False, indent=2)
                )
            except TypeError as e:
                logger.error(f"Error dumping global_general_data: {e}")
        else:
            logger.debug("Global General Data: None")

        # 處理 profile_map
        if self._profile_map is not None:
            try:
                logger.debug(
                    "\n"
                    + "Profile Map:\n"
                    + json.dumps(self._profile_map, ensure_ascii=False, indent=2)
                )
            except TypeError as e:
                logger.error(f"Error dumping profile_map: {e}")
        else:
            logger.debug("Profile Map: None") # 實際上 profile_map 通常不會是 None 因為有預設值

        # 處理 scenario_map
        if self._scenario_map is not None:
            try:
                logger.debug(
                    "\n"
                    + "Scenario Map:\n"
                    + json.dumps(self._scenario_map, ensure_ascii=False, indent=2)
                )
            except TypeError as e:
                logger.error(f"Error dumping scenario_map: {e}")
        else:
            logger.debug("Scenario Map: None") # 實際上 scenario_map 通常不會是 None 因為有預設值

        logger.debug("\n--- Dump Complete ---")
