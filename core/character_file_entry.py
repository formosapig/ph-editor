# ph-editor/core/character_file_entry.py
import logging
import os
import copy

from typing import Dict, Any

from utils.utils import sanitize_filename

from .character_data import CharacterData
from .constants import PLAYHOME_MARKER, SpecialScenario
from .extra_data_manager import ExtraDataManager

logger = logging.getLogger(__name__)
#logger.disabled = True

'''
    sn: 7Z87BCA2 唯一識別碼，在所有的附加資料內使用
    file_id: 物理識別碼， save / load 及遊戲內辨識使用
    filename: scanpath//[file_id].png 完整檔名...看是不是要先存起來...

'''


class CharacterFileEntry:
    """ 封裝單一角色檔案資訊，包含角色 ID、完整檔案路徑、角色資料，以及快取的元數據。 """
    #_sha256_map = {}

    def __init__(
        self, file_id: str, scan_path: str, character_data: CharacterData,
        data_accessor: ExtraDataManager
    ):
        if not isinstance(character_data, CharacterData):
            raise TypeError("character_data 必須是 CharacterData 類型的實例。")

        self.file_id: str = file_id
        #self.filename: str = os.path.join(
        #    scan_path, file_id + ".png"
        #)  # 組成完整檔案路徑
        self.character_data: CharacterData = character_data
        
        #if not self.scenario_id is None:
        #logger.debug("\n" + repr(self))
        self.data_source = data_accessor
        
        #metadata = self.data_source.get_metadata(self.file_id)
        sn, metadata = self.data_source.find_metadata_by_file_id(self.file_id)
        self.sn = sn
        if metadata is None:
            # metadata 為 None 時的處理方式
            self.profile_id = None
            self.scenario_id = None
            self.remark = "" # 空字串...
            self.status = "draft"
            self.tag_id = None
            self.backstage_data = {}
        else:
            # 使用 .get() 方法安全地存取字典鍵值，避免 KeyError
            self.profile_id = metadata.get('!profile_id')
            self.scenario_id = metadata.get('!scenario_id')
            self.remark = metadata.get('!remark', "")
            self.status = metadata.get('!status', "draft")
            # 存取巢狀字典時，也使用 .get() 來確保安全
            self.backstage_data = metadata.get('backstage', {})
            self.tag_id = self.backstage_data.get('!tag_id')
        
    ''' 以下是一堆 getter '''
    def get_profile_name(self) -> str:
        """ Profile 資料中取得 name """
        if self.profile_id is None:
            return ""

        profile_data: Dict[str, Any] = self.data_source.get_profile(self.profile_id)
        if not profile_data:
            raise ValueError(
                f"❌ 無法從 Profile ID '{self.profile_id}' 取得有效的 Profile 資料。"
            )

        name = profile_data.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ValueError(
                f"❌ Profile ID '{self.profile_id}' 的 'name' 欄位無效或為空。"
            )
                
        return name.strip()
    
    def get_scenario_scene(self) -> str:
        """ Scenario 資料中取得 scene(標題) """
        if self.scenario_id is None:
            return ""

        # 特殊 scenario id 都濾掉
        if self.scenario_id in [SpecialScenario.NEW, SpecialScenario.SILHOUETTE, SpecialScenario.REVERBERATION]:
            return ""

        scenario_data: Dict[str, Any] = self.data_source.get_scenario(self.scenario_id)
        if not scenario_data:
            raise ValueError(
                f"❌ 無法從 Scenario ID '{self.scenario_id}' 取得有效的 Scenario 資料。"
            )

        scene = scenario_data.get("scene")
        if not isinstance(scene, str) or not scene.strip():
            raise ValueError(
                f"❌ Scenario ID '{self.scenario_id}' 的 'scene' 欄位無效或為空。"
            )
                
        return scene.strip()

    def get_character_title(self) -> str:
        """ character 的 title 存放在 metadta.backstage """
        metadata:Dict[str, any] = self.data_source.get_metadata(self.sn)
        if metadata is None:
            return ""
        else:
            return metadata.get('backstage', {}).get('title', "").strip()

    def get_resonance(self) -> str:
        metadata:Dict[str, any] = self.data_source.get_metadata(self.sn)
        if metadata is None:
            return ""
        else:
            return metadata.get('backstage', {}).get('resonance', "").strip()
    
    def get_tag_name(self) -> str:
        metadata:Dict[str, any] = self.data_source.get_metadata(self.sn)
        if metadata is None:
            return ""
        else:
            return metadata.get('backstage', {}).get('tag', "").strip()

    def get_filename(self) -> str:
        return self.filename

    def get_character_data(self) -> dict:
        """ 獲取並整合角色所有相關資料為一個字典，供前端使用。 """
        full_data = copy.deepcopy(self.character_data.parsed_data)

        story = {
            'profile': self.data_source.get_profile(self.profile_id),
            'scenario': self.data_source.get_scenario(self.scenario_id),
            'backstage': self.data_source.get_metadata(self.sn).get('backstage', {})
        }
        full_data['story'] = story

        return full_data

    def get_profile(self) -> dict:
        return self.data_source.get_profile(self.profile_id)

    def get_scenario(self) -> dict:
        return self.data_source.get_scenario(self.scenario_id)
        
    def update_profile_id(self, profile_id: int):
        self.profile_id = profile_id
        self.data_source.update_profile_id(self.sn, profile_id)
        
    def update_scenario_id(self, scenario_id: int):
        self.scenario_id = scenario_id
        self.data_source.update_scenario_id(self.sn, scenario_id)

    def remove_scenario(self):
        self.scenario_id = None
        self.data_source.remove_scenario(self.sn)

    def update_character_data(self, main_key: str, sub_key: str, data: any):
        self.character_data.update_data(main_key, sub_key, data)
        self.save()
        
    def update_tag_id(self, tag_id: int):
        self.tag_id = tag_id

    def update_remark(self, remark: str):
        self.remark = remark
        self.data_source.update_remark(self.sn, remark)

    def get_remark(self) -> str:
        return self.remark

    def update_status(self, status: str):
        valid_statuses = ["archived", "draft", "refinement", "finalized"]
        if status not in valid_statuses:
            logger.warning(f"嘗試設定無效的狀態: {status}，已忽略。")
            return
        self.status = status
        self.data_source.update_status(self.sn, status)

    def get_status(self) -> str:
        """取得目前檔案的製作狀態 (draft, refinement, finalized)。 預設是 draft"""
        if not self.status:
            self.status = "draft"
        return self.status

    def change_file_id(self, new_id: str):
        """
        更新 file_id ， 並同步更新 medadata (JSON) 。
        注意：此方法應在實體檔案 rename 成功後才呼叫。
        """
        self.file_id = new_id
        self.data_source.update_file_id(self.sn, new_id)
        logger.debug(f"更新為: {self.file_id}")    

    def remove_metadata(self):
        try:
            self.data_source.remove_metadata(self.sn)
        except Exception as e:
            logger.error(f"刪除 metadata 失敗: {e}")
            raise RuntimeError(f"刪除 metadata 失敗: {e}")
        
        logger.info(f"刪除 Metadata : {self.file_id}")    
        
    def get_suggest_file_id(self) -> str:
        """
        根據角色、場景（真實、歲月迴響、時光剪影）或標籤資料，生成建議檔名。
        """
        default_file_id = "未知"
        
        if self.profile_id is None or self.scenario_id is None:
            return default_file_id

        profile_data = self.get_profile()
        if not profile_data:
            return default_file_id

        profile_name = profile_data.get("name", "")
        title = (self.get_character_title() or "").strip()
        scenario_data = self.get_scenario()
        
        result = ""
        # --- 規則 1: 歲月迴響 (REVERBERATION) ---
        if self.scenario_id == SpecialScenario.REVERBERATION:
            result = f"{profile_name}({self.get_resonance()})【{title}】"

        # --- 規則 2: 時光剪影 (SILHOUETTE) ---
        elif self.scenario_id == SpecialScenario.SILHOUETTE:
            result = f"{self.get_tag_name()}『{profile_name}』【{title}】"

        # --- 規則 3: 真實場景 (scenario_id > 0) ---
        elif self.scenario_id > 0 and scenario_data:
            born_year = profile_data.get("born")
            scenario_year = scenario_data.get("year")
            age_str = ""
            
            if born_year and scenario_year:
                try:
                    age = int(scenario_year) - int(born_year)
                    age_str = f"({age})"
                except (ValueError, TypeError):
                    pass
            
            result = f"{profile_name}{age_str}【{title}】"
        else:    
            return default_file_id
        
        return sanitize_filename(result)

    def to_dict(self, tag_resolver=None):
        meat = 0
        form = 0
        code = 0

        if self.file_id == self.get_suggest_file_id():
            code = code + 1

        t_style, t_name = tag_resolver(self.sn) if tag_resolver else ("", "")
        res = {
            "sn": self.sn,
            "file_id": self.file_id,
            "profile_name": self.get_profile_name(),
            "scenario_scene": self.get_scenario_scene(),
            "remark": self.get_remark(),
            "status": self.get_status(),
            "tag_style": t_style,
            "tag_name": t_name,
            "soul": self.calculate_soul(),
            "meat": meat,
            "form": form,
            "code": code
        }
        if self.scenario_id in [SpecialScenario.REVERBERATION, SpecialScenario.SILHOUETTE]:
            res["ccm_managed"] = True;
        #res["epoch_managed"] = True;
        return res;

    def calculate_soul(self) -> int:
        soul = 0
        if self.profile_id is not None and self.profile_id != 0:
            soul += 1
        scen = self.scenario_id    
        if SpecialScenario.is_real_scene(scen):
            soul += 1 if (self.get_character_title()) else 0
        elif scen == SpecialScenario.SILHOUETTE:
            soul += 1 if (self.get_tag_name()) else 0
        elif scen == SpecialScenario.REVERBERATION:
            soul += 1 if (self.get_resonance()) else 0
        return soul

    def __repr__(self):
        lines = [
            f"{'SN':>14}: {self.sn}",
            f"{'File ID':>14}: {self.file_id}",
            #f"{'Filename':>14}: {self.filename}",
            f"{'Profile ID':>14}: {self.profile_id}",
            f"{'Scenario ID':>14}: {self.scenario_id}",
            f"{'Tag ID':>14}: {self.tag_id}",
            f"{'Remark':>14}: {self.remark}",
            f"{'Status':>14}: {self.status}",
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

        logger.info(f"儲存 {self.filename} 成功")

    @classmethod
    def load(
        cls, scan_path: str, file_id: str, data_accessor: ExtraDataManager
    ) -> "CharacterFileEntry":
        """ 從檔案讀取角色資料，建立並回傳 CharacterFileEntry 實例。 """
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