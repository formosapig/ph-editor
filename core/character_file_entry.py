# ph-editor/core/character_file_entry.py
from datetime import datetime
import logging
import os
import copy

from typing import Dict, Any

from game_data.body_data import calculate_value_by_height
from game_data.cup_data import get_sister_cup_value
from utils.utils import get_nested_value, sanitize_filename

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
        self.filename: str = os.path.join(
            scan_path, file_id + ".png"
        )  # 組成完整檔案路徑
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
            self.tag_id = None
            self.backstage_data = {}
        else:
            # 使用 .get() 方法安全地存取字典鍵值，避免 KeyError
            self.profile_id = metadata.get('!profile_id')
            self.scenario_id = metadata.get('!scenario_id')
            self.remark = metadata.get('!remark', "")
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
    
    def get_profile_born(self) -> int:
        """ Profile 資料中取得 born """
        if self.profile_id is None:
            return 1911

        profile_data: Dict[str, Any] = self.data_source.get_profile(self.profile_id)
        if not profile_data:
            raise ValueError(
                f"❌ 無法從 Profile ID '{self.profile_id}' 取得有效的 Profile 資料。"
            )

        born = profile_data.get("born")
        if not isinstance(born, int):
            raise ValueError(
                f"❌ Profile ID '{self.profile_id}' 的 'born' 欄位無效或為空。"
            )
                
        return born

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

        # 是歲月迴響時，也濾掉
        if scenario_data.get("!echo"):
            return ""

        scene = scenario_data.get("scene")
        if not isinstance(scene, str) or not scene.strip():
            raise ValueError(
                f"❌ Scenario ID '{self.scenario_id}' 的 'scene' 欄位無效或為空。"
            )
                
        return scene.strip()

    def is_reverberation(self) -> bool:
        """ Scenario 資料中取得 !echo """
        if self.scenario_id is None:
            return False

        # 特殊 scenario id 都濾掉
        if self.scenario_id in [SpecialScenario.NEW, SpecialScenario.SILHOUETTE, SpecialScenario.REVERBERATION]:
            return False

        scenario_data: Dict[str, Any] = self.data_source.get_scenario(self.scenario_id)
        if not scenario_data:
            raise ValueError(
                f"❌ 無法從 Scenario ID '{self.scenario_id}' 取得有效的 Scenario 資料。"
            )

        return scenario_data.get("!echo") == 1

    def get_character_title(self) -> str:
        """ character 的 title 存放在 metadta.backstage """
        metadata:Dict[str, any] = self.data_source.get_metadata(self.sn)
        if metadata is None:
            return ""
        else:
            return metadata.get('backstage', {}).get('title', "").strip()

    def get_character_detail(self) -> str:
        """ character 的 detail 存放在 metadta.backstage """
        metadata:Dict[str, any] = self.data_source.get_metadata(self.sn)
        if metadata is None:
            return ""
        else:
            return metadata.get('backstage', {}).get('detail', "").strip()

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
    
    def get_backstage(self) -> dict:
        return self.data_source.get_metadata(self.sn).get('backstage', {})
        
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

    def change_file_id(self, new_id: str):
        """
        更新 file_id ， 並同步更新 medadata (JSON) 。
        注意：此方法應在實體檔案 rename 成功後才呼叫。
        """
        self.file_id = new_id
        self.data_source.update_file_id(self.sn, new_id)
        #logger.debug(f"更新為: {self.file_id}")    

    def remove_metadata(self):
        try:
            self.data_source.remove_metadata(self.sn)
        except Exception as e:
            logger.error(f"刪除 metadata 失敗: {e}")
            raise RuntimeError(f"刪除 metadata 失敗: {e}")
        
        logger.info(f"刪除 Metadata : {self.file_id}")    
        
    def get_suggest_file_id(self) -> tuple[bool,str]:
        """
        根據角色、場景（真實、歲月迴響、時光剪影）或標籤資料，生成建議檔名。
        """
                
        # 確保角色檔案
        if self.profile_id is None or not (profile_data := self.get_profile()):
            return False, "角色檔案缺失"
        
        if self.scenario_id is None or not (scenario_data := self.get_scenario()):
            return False, "場景資料缺失"

        profile_name = profile_data.get("name", "")
        title = (self.get_character_title() or "").strip()
                
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
            return False, "無效的場景資料"
        
        return True, sanitize_filename(result)

    def to_dict(self, tag_resolver=None):
        soul = self.calculate_soul()
        meat = self.calculate_meat()
        form = 0
        code = self.calculate_code()

        t_style, t_name = tag_resolver(self.sn) if tag_resolver else ("", "")
        res = {
            "sn": self.sn,
            "file_id": self.file_id,
            "profile_name": self.get_profile_name(),
            "scenario_scene": self.get_scenario_scene(),
            "remark": self.get_remark(),
            "tag_style": t_style,
            "tag_name": t_name,
            "correct": self.get_correct()[0]
            #"soul": soul,
            #"meat": meat,
            #"form": form,
            #"code": code,
            #"score": f"{(soul * 2 + 1) * (meat * 2 + 1) * (form * 2 + 1) * (code * 2 + 1):05d}"
            #"score": self.get_correct()[0]
        }
        #if self.scenario_id in [SpecialScenario.REVERBERATION, SpecialScenario.SILHOUETTE]:
        #    res["ccm_managed"] = True;
        #res["epoch_managed"] = True;
        return res;

    def calculate_soul(self) -> int:
        soul = 0
        if self.profile_id is not None and self.profile_id != 0:
            soul += 1
        scen = self.scenario_id    
        if SpecialScenario.is_real_scene(scen):
            soul += 1
        elif scen == SpecialScenario.SILHOUETTE:
            soul += 1 if (self.get_tag_name()) else 0
        elif scen == SpecialScenario.REVERBERATION:
            soul += 1 if (self.get_resonance()) else 0
        if self.get_character_title():
            soul += 1
        if self.get_character_detail():
            soul += 1    
        return soul
    
    def calculate_meat(self) -> int:
        meat = 0
        profile = self.get_profile()
        data = self.character_data.get_data()
        # 身高設定
        val_origin_height = profile.get('height', 0)
        val_setting_height = calculate_value_by_height(val_origin_height)
        val_game_height = get_nested_value(data, "body.overall.height", -1)
        if val_setting_height == val_game_height:
            meat += 1
        # 罩杯設定
        val_origin_cup = profile.get('cup', "")
        val_setting_cup = get_sister_cup_value(val_origin_cup)
        val_game_cup = get_nested_value(data, "body.breast.size", -1)
        if val_setting_cup == val_game_cup:
            meat += 1
        return meat

    def calculate_code(self) -> int:
        code = 0

        # 檔名正規化
        if self.file_id == self.get_suggest_file_id()[1]:
            code += 1
        
        # 在 metadata 修改好, 修改了 png
        metadata = self.data_source.get_metadata(self.sn)
        meta_timestamp = metadata.get('modified') if metadata else None
        if meta_timestamp is None or not os.path.exists(self.filename):
            return code

        file_mtime = int(os.path.getmtime(self.filename))
        if file_mtime > meta_timestamp:
            code += 1

        return code

    def get_correct(self) -> tuple[int, str]:
        correct_count = 0
        result_lines = []
        
        # profile
        if self.profile_id is None or self.profile_id == 0:
            correct_count += 1
            result_lines.append(
                f"❌ 簡介 : 無角色"
            )

        # scenario
        if not SpecialScenario.is_valid_scene(self.scenario_id):
            correct_count += 1
            result_lines.append(
                f"❌ 場景 : 不存在"
            )

        # backstage
        if not self.get_tag_name():
            correct_count += 1
            result_lines.append(
                f"❌ 標籤 : 未選擇"
            )


        if not self.get_character_title():
            correct_count += 1
            result_lines.append(
                f"❌ 標題 : 無"
            )
        if not self.get_character_detail():
            correct_count += 1
            result_lines.append(
                f"❌ 細節 : 無"
            )

        profile = self.get_profile()
        data = self.character_data.get_data()
        
        # 身高設定
        val_origin_height = profile.get('height', 0)
        val_setting_height = calculate_value_by_height(val_origin_height)
        val_game_height = get_nested_value(data, "body.overall.height", -1)
        
        # 只有數字不對時才輸出
        if val_setting_height != val_game_height:
            correct_count += 1
            result_lines.append(
                f"❌ 身高 : {val_game_height} → {val_setting_height} ({val_origin_height} cm)"
            )
        
        # 罩杯設定
        val_origin_cup = profile.get('cup', "")
        val_setting_cup = get_sister_cup_value(val_origin_cup)
        val_game_cup = get_nested_value(data, "body.breast.size", -1)
        
        # 只有數字不對時才輸出
        if val_setting_cup != val_game_cup:
            correct_count += 1
            result_lines.append(
                f"❌ 罩杯 : {val_game_cup} → {val_setting_cup} ({val_origin_cup})"
            )
        
        # 檔名正規化
        if self.file_id != (suggest := self.get_suggest_file_id())[1]:
            correct_count += 1
            result_lines.append(f"❌ 檔名 : {'→ ' + suggest[1] if suggest[0] else suggest[1]}")
            
        # 在 metadata 修改好, 修改了 png
        metadata = self.data_source.get_metadata(self.sn)
        meta_timestamp = metadata.get('modified') if metadata else None
        if meta_timestamp is not None and os.path.exists(self.filename):
            file_mtime = int(os.path.getmtime(self.filename))
            if file_mtime < meta_timestamp:
                correct_count += 1
                dt = datetime.fromtimestamp(file_mtime)
                dt_str = f"{dt.year}/{dt.month}/{dt.day} {dt.strftime('%H:%M:%S')}"            
                result_lines.append(f"❌ 修改 : {dt_str}")

        # 用換行符連接，如果都不對則回傳空字串
        return correct_count, "\n".join(result_lines)

    def __repr__(self):
        lines = [
            f"{'SN':>14}: {self.sn}",
            f"{'File ID':>14}: {self.file_id}",
            #f"{'Filename':>14}: {self.filename}",
            f"{'Profile ID':>14}: {self.profile_id}",
            f"{'Scenario ID':>14}: {self.scenario_id}",
            f"{'Tag ID':>14}: {self.tag_id}",
            f"{'Remark':>14}: {self.remark}",
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

    def reload_binary(self):
        """
        僅重新讀取檔案中的 PlayHome 二進位資料並更新 character_data。
        Metadata 保持不變。
        """
        # 1. 重新讀取檔案二進位資料
        try:
            with open(self.filename, "rb") as f:
                full_png_data = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到角色檔案，無法重新載入：{self.filename}")
        except Exception as e:
            raise RuntimeError(f"讀取檔案失敗：{self.filename} -> {e}")

        # 2. 重新定位並擷取 PlayHome 資料區塊
        marker_start_pos = full_png_data.find(PLAYHOME_MARKER)
        if marker_start_pos == -1:
            raise ValueError(f"檔案中未找到 PlayHome 標記：{self.filename}")

        raw_data_with_marker = full_png_data[marker_start_pos:]

        # 3. 更新 character_data 實例
        try:
            self.character_data = CharacterData(raw_data_with_marker)
        except Exception as e:
            raise ValueError(f"無法解析重新載入的角色資料：{self.filename} -> {e}")

        #logger.info(f"成功重新載入角色二進位資料：{self.file_id}")

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