# ph-editor/core/character_file_entry.py
import logging
import os
import hashlib
import copy

from typing import Dict, Any

from .character_data import CharacterData
from .file_constants import PLAYHOME_MARKER
from .extra_data_manager import ExtraDataManager

logger = logging.getLogger(__name__)
#logger.disabled = True


class CharacterFileEntry:
    """
    封裝單一角色檔案資訊，包含角色 ID、完整檔案路徑、角色資料，以及快取的元數據。
    """
    #_sha256_map = {}

    def __init__(
        self, file_id: str, scan_path: str, character_data: CharacterData,
        data_accessor: ExtraDataManager
    ):
        # 取得 int 小函式
        def _get_int(data, *keys):
            for key in keys:
                if not isinstance(data, dict):
                    return None
                data = data.get(key)
            return data if isinstance(data, int) else None

        if not isinstance(character_data, CharacterData):
            raise TypeError("character_data 必須是 CharacterData 類型的實例。")

        self.file_id: str = file_id
        self.filename: str = os.path.join(
            scan_path, file_id + ".png"
        )  # 組成完整檔案路徑
        self.character_data: CharacterData = character_data
        self.save_flag: bool = False  # 預設不需儲存
        self.sync_flag: bool = False  # 預設不需同步資料
        
        #if not self.scenario_id is None:
        #logger.debug("\n" + repr(self))
        self.data_source = data_accessor
        
        metadata = self.data_source.get_metadata(self.file_id)
        
        if metadata is None:
            # metadata 為 None 時的處理方式
            self.profile_id = None
            self.scenario_id = None
            self.tag_id = None
        else:
            # 使用 .get() 方法安全地存取字典鍵值，避免 KeyError
            self.profile_id = metadata.get('!profile_id')
            self.scenario_id = metadata.get('!scenario_id')
            
            # 存取巢狀字典時，也使用 .get() 來確保安全
            backstage_data = metadata.get('backstage', {})
            self.tag_id = backstage_data.get('!tag_id')
        
    ''' 以下是一堆 getter '''
    def get_profile_name(self) -> str:
        """從關聯的 Profile 資料中取得名稱。"""
        # 檢查 profile_id 是否存在
        if self.profile_id is None:
            return ""

        # 這裡假設 self.data_source.get_profile 
        # 在找不到資料時會回傳空字典 {}
        profile_data: Dict[str, Any] = self.data_source.get_profile(self.profile_id)
        
        # 檢查回傳的字典是否為空
        if not profile_data:
            raise ValueError(
                f"❌ 無法從 Profile ID '{self.profile_id}' 取得有效的 Profile 資料。"
            )

        # 安全地取得名稱，如果不存在則回傳 None
        name = profile_data.get("name")
        
        # 檢查名稱是否為有效的字串，並處理空白字串
        if not isinstance(name, str) or not name.strip():
            raise ValueError(
                f"❌ Profile ID '{self.profile_id}' 的 'name' 欄位無效或為空。"
            )
                
        return name.strip()
    
    def get_scenario_title(self) -> str:
        """從關聯的 Scenario 資料中取得名稱。"""
        # 檢查 scenario_id 是否存在
        if self.scenario_id is None:
            return ""

        # 這裡假設 self.data_source.get_scenario
        # 在找不到資料時會回傳空字典 {}
        scenario_data: Dict[str, Any] = self.data_source.get_scenario(self.scenario_id)
        
        # 檢查回傳的字典是否為空
        if not scenario_data:
            raise ValueError(
                f"❌ 無法從 Scenario ID '{self.scenario_id}' 取得有效的 Scenario 資料。"
            )

        # 安全地取得名稱，如果不存在則回傳 None
        title = scenario_data.get("title")
        
        # 檢查名稱是否為有效的字串，並處理空白字串
        if not isinstance(title, str) or not title.strip():
            raise ValueError(
                f"❌ Scenario ID '{self.scenario_id}' 的 'title' 欄位無效或為空。"
            )
                
        return title.strip()
        
    def set_sync_flag(self, value: bool = True):
        self.sync_flag = value

    def needs_syncing(self) -> bool:
        return self.sync_flag

    def set_save_flag(self, value: bool = True):
        self.save_flag = value

    def needs_saving(self) -> bool:
        return self.save_flag

    def get_filename(self) -> str:
        return self.filename

    #def get_character_data(self) -> CharacterData:
    #    return self.character_data

    def get_character_data(self) -> dict:
        """
        獲取並整合角色所有相關資料為一個字典。
        """
        # 創建 parsed_data 的深度複製，避免修改原始資料。
        # dict 本身沒有 deep_copy 方法，需要使用 copy 模組。
        full_data = copy.deepcopy(self.character_data.parsed_data)

        # 建立一個新的字典來存放故事相關資料
        story = {
            'profile': self.data_source.get_profile(self.profile_id),
            'scenario': self.data_source.get_scenario(self.scenario_id),
            'backstage': self.data_source.get_metadata(self.file_id).get('backstage', {})
        }

        # 將故事字典合併到主字典中
        full_data['story'] = story

        return full_data

    def get_profile(self) -> dict:
        if isinstance(self.character_data.parsed_data, dict):
            story = self.character_data.parsed_data.get("story", {})
            profile = story.get("profile")
            if isinstance(profile, dict):
                return profile
        return {}

    def get_scenario(self) -> dict:
        if isinstance(self.character_data.parsed_data, dict):
            story = self.character_data.parsed_data.get("story", {})
            scenario = story.get("scenario")
            if isinstance(scenario, dict):
                return scenario
        return {}
        
    def update_profile_id(self, profile_id: int):
        self.profile_id = profile_id
        self.data_source.update_profile_id(self.file_id, profile_id)
        
    def update_scenario_id(self, scenario_id: int):
        self.scenario_id = scenario_id
        self.data_source.update_scenario_id(self.file_id, scenario_id)

    def update_character_data(self, main_key: str, sub_key: str, data: any):
        self.character_data.update_data(main_key, sub_key, data)
        
    def update_tag_id(self, tag_id: int):
        self.tag_id = tag_id

    def __repr__(self):
        lines = [
            f"{'File ID':>14}: {self.file_id}",
            f"{'Filename':>14}: {self.filename}",
            f"{'Save Flag':>14}: {self.save_flag}",
            f"{'Sync Flag':>14}: {self.sync_flag}",
            f"{'Profile ID':>14}: {self.profile_id}",
            f"{'Scenario ID':>14}: {self.scenario_id}",
            f"{'Tag ID':>14}: {self.tag_id}",
        ]
        return "\n".join(lines)

    def save(self, individual_only=False):
        # 取得最新 PlayHome 自訂資料 bytes (包含 marker)
        playhome_data = self.character_data.to_raw_data()

        try:
            with open(self.filename, "rb") as f:
                full_png_data = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到角色檔案：{self.filename}")

        marker_pos = full_png_data.find(PLAYHOME_MARKER)
        if marker_pos == -1:
            raise ValueError(f"檔案中未找到 PlayHome 標記：{self.filename}")

        png_part = full_png_data[:marker_pos]

        combined_data = png_part + playhome_data

        try:
            with open(self.filename, "wb") as f:
                f.write(combined_data)
        except Exception as e:
            raise IOError(f"寫入檔案失敗：{self.filename} -> {e}")

        self.save_flag = False
        if not individual_only:
            self.sync_flag = False

    @classmethod
    def load(
        cls, scan_path: str, file_id: str, data_accessor: ExtraDataManager
    ) -> "CharacterFileEntry":
        """
        從檔案讀取角色資料，建立並回傳 CharacterFileEntry 實例。
        """
        file_name_with_ext = file_id + ".png"
        file_path = os.path.join(scan_path, file_name_with_ext)

        try:
            with open(file_path, "rb") as f:
                full_png_data = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到角色檔案：{file_path}")
        except Exception as e:
            raise RuntimeError(f"讀取角色檔案時發生錯誤：{file_path} -> {e}")

        marker_start_pos = full_png_data.find(PLAYHOME_MARKER)
        if marker_start_pos == -1:
            raise ValueError(f"檔案中未找到 PlayHome 標記：{file_path}")

        raw_data_with_marker = full_png_data[marker_start_pos:]

        # 1. 對 raw_data_with_marker 做 sha256
        #sha256_hash = hashlib.sha256(raw_data_with_marker).hexdigest()

        # 2. 對一個 map 檢查 sha256，若存在時，dump 對應的 file_id
        #if sha256_hash in cls._sha256_map:
        #    existing_file_id = cls._sha256_map[sha256_hash]
        #    logger.debug(f"{file_id} duplicate with {existing_file_id}")
            # 你可以選擇在這裡拋出異常、跳過或返回現有的實例，
            # 這裡只是打印消息並繼續處理，讓調用者決定如何應對重複。
            # 如果你希望重複時直接停止或返回現有對象，請修改這裡。
            # 例如：raise ValueError(f"檔案 {file_id} 與 {existing_file_id} 重複！")
            # 或者：return cls._sha256_map[sha256_hash] # 如果你的map存的是CharacterFileEntry實例

        #else:
            # 3. 若沒有重複，將 (file_id, sha256) 存入 map
        #    cls._sha256_map[sha256_hash] = file_id

        try:
            character_data_obj = CharacterData(raw_data_with_marker)
        except Exception as e:
            raise ValueError(f"無法解析角色資料：{file_path} -> {e}")

        return cls(file_id, scan_path, character_data_obj, data_accessor)
