# ph-editor/core/user_config_manager.py
import os
import json
import logging

logger = logging.getLogger(__name__)
#logger.disabled = True


class UserConfigManager:
    config_dir = "user_config"
    scan_path_file = os.path.join(config_dir, "scan_path.txt")
    cache_dir = os.path.join(config_dir, "cache")  # ✅ 加入 cache 目錄
    general_file = os.path.join(config_dir, "general.json")
    profile_file = os.path.join(config_dir, "profile.json")
    scenario_file = os.path.join(config_dir, "scenario.json")
    metadata_file = os.path.join(config_dir, "metadata.json")

    # 注意, makedirs 在目錄己存在時,不會報錯且執行效率高,一直亂呼叫也沒什麼成本.
    @staticmethod
    def ensure_dir():
        os.makedirs(UserConfigManager.config_dir, exist_ok=True)
        os.makedirs(
            UserConfigManager.cache_dir, exist_ok=True
        )  # ✅ 保證 cache 資料夾也存在

    @staticmethod
    def get_cache_dir() -> str:
        UserConfigManager.ensure_dir()
        return UserConfigManager.cache_dir

    @staticmethod
    def load_scan_path() -> str | None:
        UserConfigManager.ensure_dir()
        if not os.path.exists(UserConfigManager.scan_path_file):
            return None
        with open(UserConfigManager.scan_path_file, "r", encoding="utf-8") as f:
            return f.read().strip()

    @staticmethod
    def save_scan_path(path_str: str):
        UserConfigManager.ensure_dir()
        with open(UserConfigManager.scan_path_file, "w", encoding="utf-8") as f:
            f.write(path_str)

    @staticmethod
    def get_general_file_path() -> str:
        UserConfigManager.ensure_dir()
        return UserConfigManager.general_file

    @staticmethod
    def get_profile_file_path() -> str:
        UserConfigManager.ensure_dir()
        return UserConfigManager.profile_file

    @staticmethod
    def get_scenario_file_path() -> str:
        UserConfigManager.ensure_dir()
        return UserConfigManager.scenario_file

    @staticmethod
    def get_metadata_file_path() -> str:
        UserConfigManager.ensure_dir()
        return UserConfigManager.metadata_file
    
    @staticmethod
    def load_json_file(file_path: str) -> dict:
        """載入指定路徑的 JSON 檔案，若失敗則拋出異常。"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"找不到檔案: {file_path}")
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"讀取或解析 JSON 檔案失敗: {file_path} -> {e}")
            raise e

    # ✅ 新增的儲存方法
    @staticmethod
    def save_json_file(file_path: str, data: dict):
        """
        將字典資料儲存為 JSON 檔案。
        Args:
            file_path: 檔案路徑。
            data: 要儲存的字典資料。
        """
        # 在寫入前確保目錄存在
        UserConfigManager.ensure_dir()
        
        # 檢查資料鍵的類型，如果為 int，則轉換為 str
        # 這裡假設所有鍵都是同一類型，這是基於你的使用情境
        converted_data = {}
        if data:
            first_key = next(iter(data))
            if isinstance(first_key, int):
                converted_data = {str(k): v for k, v in data.items()}
            else:
                converted_data = data
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                # 使用 indent 讓檔案更易讀
                json.dump(converted_data, f, indent=2, ensure_ascii=False)
            logger.info(f"檔案已成功儲存: {file_path}")
        except IOError as e:
            logger.error(f"儲存檔案失敗: {file_path} -> {e}")
            raise e
            
# 測試用
if __name__ == "__main__":
    print("scan_path:", UserConfigManager.load_scan_path())
    UserConfigManager.save_scan_path("D:/illusion/PlayHome/UserData/Chara")
    print("寫入 scan_path 完成")
