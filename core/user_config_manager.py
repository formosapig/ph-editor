# ph-editor/core/user_config_manager.py
import os


class UserConfigManager:
    config_dir = "user_config"
    scan_path_file = os.path.join(config_dir, "scan_path.txt")
    cache_dir = os.path.join(config_dir, "cache")  # ✅ 加入 cache 目錄

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


# 測試用
if __name__ == "__main__":
    print("scan_path:", UserConfigManager.load_scan_path())
    UserConfigManager.save_scan_path("D:/illusion/PlayHome/UserData/Chara")
    print("寫入 scan_path 完成")
