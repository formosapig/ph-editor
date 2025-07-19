# ph-editor/core/character_file_entry.py
import logging
import os

from .character_data import CharacterData
from .file_constants import PLAYHOME_MARKER

logger = logging.getLogger(__name__)


class CharacterFileEntry:
    """
    封裝單一角色檔案資訊，包含角色 ID、完整檔案路徑、角色資料，以及快取的元數據。
    """

    def __init__(
        self, character_id: str, scan_path: str, character_data: CharacterData
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

        self.character_id: str = character_id
        self.filename: str = os.path.join(
            scan_path, character_id + ".png"
        )  # 組成完整檔案路徑
        self.character_data: CharacterData = character_data
        self.save_flag: bool = False  # 預設不需儲存
        self.sync_flag: bool = False  # 預設不需同步資料

        if isinstance(character_data.parsed_data, dict):
            story = character_data.parsed_data.get("story", {})
            self.general_version = _get_int(story, "general", "!version")
            self.profile_version = _get_int(story, "profile", "!version")
            self.profile_id = _get_int(story, "profile", "!id")

        self.display_name = "測試中"
        # logger.debug(self)

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

    def __repr__(self):
        lines = [
            f"{'Character ID':>16}: {self.character_id}",
            f"{'Filename':>16}: {self.filename}",
            f"{'Save Flag':>16}: {self.save_flag}",
            f"{'Sync Flag':>16}: {self.sync_flag}",
            f"{'General Version':>16}: {self.general_version}",
            f"{'Profile Version':>16}: {self.profile_version}",
            f"{'Profile ID':>16}: {self.profile_id}",
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
    def load(cls, scan_path: str, character_id: str) -> "CharacterFileEntry":
        """
        從檔案讀取角色資料，建立並回傳 CharacterFileEntry 實例。
        """
        file_name_with_ext = character_id + ".png"
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

        return cls(character_id, scan_path, character_data_obj)


# 範例用法 (僅供測試參考，實際應用會在後端框架中調用)
if __name__ == "__main__":
    # 假設您有一個 CharacterData 類別的簡易實現，用於測試
    class MockCharacterData:
        def __init__(self, global_version: str, display_name: str):
            self.global_data = {"general_version": global_version}
            self.metadata = {"display_name": display_name}

        # 假設 CharacterData 還有其他方法，例如解析器和序列化器會用到 BytesIO
        # 為簡化範例，這裡省略具體實現

    logger.info("--- 測試 CharacterFileEntry ---")

    # 創建一個 CharacterData 實例
    mock_data_1 = MockCharacterData(global_version="1.0.0", display_name="勇者艾倫")

    # 創建 CharacterFileEntry
    entry1 = CharacterFileEntry("character_001.bin", mock_data_1)
    print(f"初始化 entry1: {entry1}")
    print(f"entry1.needs_saving(): {entry1.needs_saving()}")
    print(f"entry1.general_version: {entry1.general_version}")
    print(f"entry1.display_name: {entry1.display_name}")

    entry1.set_save_flag(True)
    print(f"設定 save_flag 後 entry1.needs_saving(): {entry1.needs_saving()}")

    print("\n--- 測試另一個 CharacterFileEntry ---")
    mock_data_2 = MockCharacterData(global_version="1.0.1", display_name="魔法師莉莉")
    entry2 = CharacterFileEntry("character_002.bin", mock_data_2)
    print(f"初始化 entry2: {entry2}")
    print(f"entry2.needs_saving(): {entry2.needs_saving()}")
    print(f"entry2.general_version: {entry2.general_version}")
    print(f"entry2.display_name: {entry2.display_name}")

    # 測試缺少某些數據的 CharacterData
    class IncompleteMockCharacterData:
        def __init__(self):
            self.global_data = {}  # 缺少 general_version
            self.metadata = {}  # 缺少 display_name

    print("\n--- 測試不完整數據的 CharacterFileEntry ---")
    incomplete_data = IncompleteMockCharacterData()
    incomplete_entry = CharacterFileEntry("incomplete.bin", incomplete_data)
    print(f"初始化 incomplete_entry: {incomplete_entry}")
    print(
        f"incomplete_entry.general_version: {incomplete_entry.general_version}"
    )  # 應該是 None
    print(
        f"incomplete_entry.display_name: {incomplete_entry.display_name}"
    )  # 應該是 None

    # 測試傳入非 CharacterData 類型的錯誤
    try:
        CharacterFileEntry("wrong_type.bin", "這不是CharacterData")
    except TypeError as e:
        print(f"\n捕獲到預期的錯誤: {e}")
