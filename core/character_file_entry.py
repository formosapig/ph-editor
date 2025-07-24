# ph-editor/core/character_file_entry.py
import logging
import os

from .character_data import CharacterData
from .file_constants import PLAYHOME_MARKER

logger = logging.getLogger(__name__)
#logger.disabled = True


class CharacterFileEntry:
    """
    封裝單一角色檔案資訊，包含角色 ID、完整檔案路徑、角色資料，以及快取的元數據。
    """

    def __init__(
        self, file_id: str, scan_path: str, character_data: CharacterData
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

        if isinstance(character_data.parsed_data, dict):
            story = character_data.parsed_data.get("story", {})
            self.general_version = _get_int(story, "general", "!version")
            self.profile_id = _get_int(story, "profile", "!id")
            self.profile_version = _get_int(story, "profile", "!version")
            self.scenario_id = _get_int(story, "scenario", "!id")
            self.scenario_version = _get_int(story, "scenario", "!version")
            self.tag_id = _get_int(story, "backstage", "!tag_id")
        
        logger.debug("\n" + repr(self))

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

    def get_character_data(self) -> CharacterData:
        return self.character_data

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
        
    def update_tag_id(self):
        tag_id_value = None
        try:
            tag_id_value = self.character_data.parsed_data['story']['backstage'].get('!tag_id')

            if tag_id_value is not None:
                temp_tag_id = int(tag_id_value)
                self.tag_id = temp_tag_id

        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"處理 !tag_id 時發生錯誤：{e}。self.tag_id 將保持不變。")

    def __repr__(self):
        lines = [
            f"{'File ID':>14}: {self.file_id}",
            f"{'Filename':>14}: {self.filename}",
            f"{'Save Flag':>14}: {self.save_flag}",
            f"{'Sync Flag':>14}: {self.sync_flag}",
            f"{'General Ver.':>14}: {self.general_version}",
            f"{'Profile ID':>14}: {self.profile_id}",
            f"{'Profile Ver.':>14}: {self.profile_version}",
            f"{'Scenario ID':>14}: {self.scenario_id}",
            f"{'Scenario Ver.':>14}: {self.scenario_version}",
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
    def load(cls, scan_path: str, file_id: str) -> "CharacterFileEntry":
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

        try:
            character_data_obj = CharacterData(raw_data_with_marker)
        except Exception as e:
            raise ValueError(f"無法解析角色資料：{file_path} -> {e}")

        return cls(file_id, scan_path, character_data_obj)
