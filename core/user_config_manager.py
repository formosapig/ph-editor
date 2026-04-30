# ph-editor/core/user_config_manager.py
import base64
import os
import json
import logging
import zlib

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
    wish_file = os.path.join(config_dir, "wish.json")

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
    def get_wish_file_path() -> str:
        UserConfigManager.ensure_dir()
        return UserConfigManager.wish_file
    
    @staticmethod
    def _obfuscate(text: str) -> str:
        if not text: return text
        
        # 門檻設為 60 字元（大約是 look 或 about 的長度）
        # 短字串用舊的 b64，長字串才用 z64
        if len(text) < 60:
            encoded = base64.b64encode(text.encode("utf-8")).decode("utf-8")
            return f"b64:{encoded}"
        else:
            compressed = zlib.compress(text.encode("utf-8"), level=9)
            encoded = base64.b64encode(compressed).decode("utf-8")
            return f"z64:{encoded}"
    
    @staticmethod
    def _deobfuscate(text: str) -> str:
        if not isinstance(text, str):
            return text
        
        # 支援新版壓縮格式
        if text.startswith("z64:"):
            try:
                return zlib.decompress(base64.b64decode(text[4:])).decode("utf-8")
            except Exception:
                return text
                
        # 支援舊版純 Base64 格式（這樣你舊的資料才讀得回來，不會炸掉）
        elif text.startswith("b64:"):
            try:
                return base64.b64decode(text[4:]).decode("utf-8")
            except Exception:
                return text
                
        return text
    
    @staticmethod
    def _process_data(data, func):
        """遞迴處理字典或列表中的所有字串內容"""
        if isinstance(data, dict):
            return {k: UserConfigManager._process_data(v, func) for k, v in data.items()}
        elif isinstance(data, list):
            return [UserConfigManager._process_data(i, func) for i in data]
        elif isinstance(data, str):
            return func(data)
        return data

    @staticmethod
    def load_json_file(file_path: str) -> dict:
        """載入指定路徑的 JSON 檔案，若失敗則拋出異常。"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"找不到檔案: {file_path}")
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return UserConfigManager._process_data(data, UserConfigManager._deobfuscate)
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"讀取或解析 JSON 檔案失敗: {file_path} -> {e}")
            raise e

    @staticmethod
    def save_json_file(file_path: str, data: dict):
        """
        將字典資料儲存為 JSON 檔案。
        Args:
            file_path: 檔案路徑。
            data: 要儲存的字典資料。
        """
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
        
        obfuscated_data = UserConfigManager._process_data(converted_data, UserConfigManager._obfuscate)

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                # 使用 indent 讓檔案更易讀
                json.dump(obfuscated_data, f, indent=4, ensure_ascii=False)
            #logger.info(f"檔案已成功儲存: {file_path}")
        except IOError as e:
            logger.error(f"儲存檔案失敗: {file_path} -> {e}")
            raise e
        
        # --- 新增：把所有明碼資料幹掉的方法 ---
    
    @staticmethod
    def cleanup_plain_backups():
        """
        刪除 user_config 目錄下所有明碼備份檔：
        包含 .bak, .bin 結尾，以及 bin. 開頭的檔案
        """
        if not os.path.exists(UserConfigManager.config_dir):
            return

        print(f"🧹 開始清理 {UserConfigManager.config_dir} 中的明碼檔案...")
        
        count = 0
        for filename in os.listdir(UserConfigManager.config_dir):
            # 定義明碼檔案的特徵
            is_bak = filename.endswith(".bak")
            is_bin_ext = filename.endswith(".bin")
            is_bin_prefix = filename.startswith("bin.")
            
            if is_bak or is_bin_ext or is_bin_prefix:
                file_path = os.path.join(UserConfigManager.config_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f"🗑️ 已刪除: {filename}")
                        count += 1
                except Exception as e:
                    print(f"❌ 無法刪除 {filename}: {e}")
        
        print(f"✨ 清理完成，共刪除 {count} 個檔案。")
            
# --- 這是修改後的執行區塊 ---
if __name__ == "__main__":
    # 定義所有要備份的 JSON 檔案路徑
    target_files = {
        "general": UserConfigManager.get_general_file_path(),
        "profile": UserConfigManager.get_profile_file_path(),
        "scenario": UserConfigManager.get_scenario_file_path(),
        "metadata": UserConfigManager.get_metadata_file_path(),
        "wish": UserConfigManager.get_wish_file_path(),
    }

    print("=== 開始產生成明碼備份 (.bak) ===")
    
    for desc, path in target_files.items():
        if os.path.exists(path):
            try:
                # 1. 讀取並解密檔案內容
                decrypted_data = UserConfigManager.load_json_file(path)
                
                # 2. 重新構造檔名
                # dirname 拿到 "user_config"
                # basename 拿到 "general.json" -> splitext 拿到 "general"
                dir_name = os.path.dirname(path)
                file_name_full = os.path.basename(path)
                file_name_only, _ = os.path.splitext(file_name_full)
                
                # 組合成 bin.xxxx 格式
                new_filename = f"bin.{file_name_only}"
                new_path = os.path.join(dir_name, new_filename)
                
                # 3. 以明碼方式寫入
                with open(new_path, "w", encoding="utf-8") as f:
                    json.dump(decrypted_data, f, indent=4, ensure_ascii=False)
                
                print(f"✅ {desc} 轉換成功 -> {new_path}")
            except Exception as e:
                print(f"❌ {desc} 處理失敗: {e}")
        else:
            print(f"ℹ️ {desc} 不存在，跳過 (路徑: {path})")

    print("=== 備份作業完成 ===")