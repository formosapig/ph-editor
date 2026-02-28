# ph-editor/app.py
import io
import logging
import os, shutil
import re

from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    send_file,
    send_from_directory,
)
from PIL import Image

from api.character_bp import api_characters_bp
from api.profile import api_profile_bp
from api.scenario import api_scenario_bp
from api.ui_config import api_ui_config_bp
from config.logging_setup import setup_logging

# 從 shared_data 模組引入相關函式
from core.shared_data import (
    add_or_update_character_with_path,
    clear_characters_db,
    process_tag_info,
    
    initialize_extra_data,
    get_general_data,
    get_character_file_entry,
    remove_character_file_entry,
    get_wish_list,
    add_wish,
    delete_wish as delete_wish_service,
)
from core.user_config_manager import UserConfigManager
from web.arrange_bp import arrange_bp
from web.ccm_bp import ccm_bp
from web.compare_bp import compare_bp
from web.edit_bp import edit_bp
from web.general_bp import general_bp

# 初始化時確保所有目錄存在
UserConfigManager.ensure_dir()

# app = Flask(__name__)
# 建立 Flask 應用程式實例，並只設定變數的分隔符號
app = Flask(__name__, template_folder='templates')
app.jinja_env.variable_start_string = '[['
app.jinja_env.variable_end_string = ']]'
app.jinja_env.block_start_string = '[%'
app.jinja_env.block_end_string = '%]'

app.register_blueprint(arrange_bp)
app.register_blueprint(ccm_bp)
app.register_blueprint(compare_bp)
app.register_blueprint(edit_bp)
app.register_blueprint(general_bp)
app.register_blueprint(api_characters_bp)
app.register_blueprint(api_profile_bp)
app.register_blueprint(api_scenario_bp)
app.register_blueprint(api_ui_config_bp)

# 設定快取路徑
CACHE_DIR = UserConfigManager.get_cache_dir()
# 設定掃描路徑
scan_path = UserConfigManager.load_scan_path()
app.config["SCAN_PATH"] = scan_path if scan_path else ""

# 在應用程式啟動時，先設定日誌
setup_logging()

# 取得這個模組的日誌器
logger = logging.getLogger(__name__)


# ✅ 新增：在應用程式啟動時載入 general.json 資料
#logger.info("應用程式啟動，正在載入全域 general 資料...")
initialize_extra_data()
#logger.info("全域 general 資料載入完成。")


def clean_old_thumbnails(cache_dir, max_remove=3):
    if not os.path.exists(cache_dir):
        return
    files = [
        (f, os.path.getmtime(os.path.join(cache_dir, f)))
        for f in os.listdir(cache_dir)
        if f.lower().endswith((".png", ".jpg"))
    ]
    files.sort(key=lambda x: x[1])  # sort by oldest
    for f, _ in files[:max_remove]:
        try:
            os.remove(os.path.join(cache_dir, f))
            # print(f"刪除快取縮圖: {f}")
        except Exception as e:
            print(f"刪除失敗: {f}, {e}")


clean_old_thumbnails(CACHE_DIR)  # 應用啟動時執行清理


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/cache/<path:filename>")
def serve_cache(filename):
    return send_from_directory(CACHE_DIR, filename)


@app.route("/get_scan_path", methods=["GET"])
def get_scan_path():
    path = UserConfigManager.load_scan_path()
    return jsonify({"scanPath": path or ""})


@app.route("/scan", methods=["POST"])
def scan_folder():
    folder_path = request.json.get("path")

    if not folder_path:
        return jsonify({"error": "缺少資料夾路徑"}), 400

    if not os.path.isdir(folder_path):
        return jsonify({"error": "無效的資料夾路徑"}), 400

    app.config["SCAN_PATH"] = folder_path  # 更新應用程式配置中的掃描路徑
    UserConfigManager.save_scan_path(folder_path)  # ✅ 改用此處理

    # 清空現有的數據庫，以便重新掃描
    clear_characters_db()

    thumbnails = []  # 儲存生成或更新的縮圖檔案名
    loaded_character_count = 0
    character_list = []  # 儲存 thumbnail, file_id, profile_name

    logger.debug(f"開始掃描資料夾 '{folder_path}'...")
    for root, _, files in os.walk(folder_path):
        for file_name_with_ext in files:
            if file_name_with_ext.lower().endswith(".png"):
                file_path = os.path.join(root, file_name_with_ext)
                file_id = os.path.splitext(file_name_with_ext)[0]
                
                #logger.debug(f"處理 {file_id}")

                # --- 縮圖生成邏輯 ---
                
                thumbnail_name = f"thumb_{file_id}.jpg"
                '''
                thumbnail_path = os.path.join(CACHE_DIR, thumbnail_name)

                try:
                    original_mtime = os.path.getmtime(file_path)
                    if os.path.exists(thumbnail_path):
                        cache_mtime = os.path.getmtime(thumbnail_path)
                        if original_mtime <= cache_mtime:
                            thumbnails.append(thumbnail_name)
                            # print(f"  [縮圖] 快取未過期，跳過: {file_name_with_ext}")
                            pass  # 不跳過，因為還要處理角色數據
                except Exception as e:
                    print(
                        f"  [縮圖] 處理 '{file_name_with_ext}' 縮圖快取時發生錯誤: {e}"
                    )
                    # 不阻礙後續的 CharacterData 載入，但會嘗試重新生成縮圖

                # 嘗試生成/更新縮圖
                try:
                    # 如果縮圖不存在或已過期，則重新生成
                    if not os.path.exists(
                        thumbnail_path
                    ) or original_mtime > os.path.getmtime(thumbnail_path):
                        with Image.open(file_path) as img:
                            img = img.convert("RGB")
                            # img.thumbnail((189, 264)) # 等比縮圖，寬不超過189，高不超過264
                            img.save(thumbnail_path, format="JPEG", quality=85)
                        # print(f"  [縮圖] 生成/更新縮圖: {file_name_with_ext}")

                    # if thumbnail_name not in thumbnails: # 避免重複添加，如果之前快取判斷沒有跳過
                    #    thumbnails.append(thumbnail_name)

                except Exception as e:
                    print(f"  [錯誤] 生成縮圖 '{file_name_with_ext}' 失敗: {e}")
                    # 縮圖失敗不影響角色數據載入，繼續
                # --- 縮圖生成邏輯結束 ---
                # '''

                # --- 角色數據載入邏輯 ---
                
                try:
                    character_file_obj = (
                        add_or_update_character_with_path(folder_path, file_id)
                    )
                    loaded_character_count += 1
                except Exception as e:
                    logger.error(
                        f"  [錯誤] 載入或解析檔案 '{file_name_with_ext}' 的角色數據時發生錯誤: {e}"
                    )
                    continue  # 繼續處理下一個檔案
                
                character_list.append(
                    character_file_obj.to_dict(process_tag_info)
                )

    # 1. 掃描完成後, 才有確定的 tag 資料
    global_data = get_general_data()
    # dump 全域資料
    #logger.debug("全域資料：")
    #logger.debug(json.dumps(global_data, ensure_ascii=False, indent=2))

    # 2. 整理 tag type 的樣式資料
    tag_styles = global_data.get("tag_styles", {})
    tag_styles_data = {}
    for tag_type, style in tag_styles.items():
        tag_styles_data[tag_type] = {
            "color": style.get("color", "#000"),
            "bg_color": style.get("background", "#fff"),
        }

    logger.debug(
        f"掃描完成。總計處理 {len(thumbnails)} 個檔案，成功載入 {loaded_character_count} 個角色數據。"
    )
    
    # 排序
    #character_list.sort(key=lambda item: item["id"].lower())
        
    return jsonify(
        {
            "images": character_list,
            "tag_styles": tag_styles_data,
            "message": f"成功掃描 {len(thumbnails)} 個檔案並載入 {loaded_character_count} 個角色數據。",
        }
    )


@app.route("/reload_file/<file_id>", methods=["GET"])
def reload_file(file_id):
    """
    處理重新載入單個角色檔案的請求，從設定的路徑讀取數據並返回。
    """
    # 檢查 file_id 是否存在，這是 URL 路由參數
    if not file_id:
        logger.warning("reload_file 請求缺少檔案 ID。")
        return jsonify({"error": "缺少檔案 ID"}), 400

    try:
        # 1. 取得掃描路徑並嘗試更新檔案
        scan_path = app.config.get("SCAN_PATH")
        if not scan_path:
            logger.error("未設定 SCAN_PATH，無法重新載入角色檔案。")
            return jsonify({"error": "系統設定錯誤：找不到掃描路徑"}), 500
        
        # 嘗試重新載入或更新指定的檔案
        character_file_obj = add_or_update_character_with_path(scan_path, file_id)

        # 2. 檢查檔案物件是否成功返回
        if not character_file_obj:
            logger.warning(f"重新載入檔案 '{file_id}' 失敗，可能找不到該檔案。")
            return jsonify({"error": "找不到指定的檔案或處理失敗"}), 404

        # 3. 從檔案物件中提取並整理所需資料
        data_to_return = {
            "thumb": f"thumb_{file_id}.jpg",
            "id": file_id,
            "profile_name": character_file_obj.get_profile_name(),
            "scenario_title": character_file_obj.get_scenario_title(),
            "remark": character_file_obj.get_remark(),
            "status": character_file_obj.get_status(),
        }

        # 4. 處理標籤資訊，這個函式也可能出錯
        tag_style, tag_name = process_tag_info(file_id)
        data_to_return["tag_style"] = tag_style
        data_to_return["tag_name"] = tag_name

        # 5. 返回整理好的 JSON 數據
        return jsonify(data_to_return)

    except Exception as e:
        # 6. 統一處理所有未預期的錯誤
        logger.exception(f"處理檔案 '{file_id}' 時發生內部錯誤。")
        return jsonify({"error": f"處理檔案時發生內部錯誤: {str(e)}"}), 500


@app.route("/delete_files", methods=["POST"])
def delete_files():
    data = request.get_json()
    filenames_to_delete = data.get("file_ids", [])  # 改為接收多個檔名（list）

    if not filenames_to_delete or not isinstance(filenames_to_delete, list):
        return jsonify({"status": "error", "message": "未提供檔案清單或格式錯誤"}), 400

    scan_path = UserConfigManager.load_scan_path()
    if not scan_path:
        return jsonify({"status": "error", "message": "請先掃描一個資料夾"}), 400

    results = []
    for filename_to_delete in filenames_to_delete:
        full_path_original = os.path.join(scan_path, f"{filename_to_delete}.png")
        logger.debug(f"Delete {full_path_original}")
        try:
            if os.path.exists(full_path_original):
                os.remove(full_path_original)
                print(f"刪除原始檔案: {full_path_original}")
                remove_character_file_entry(filename_to_delete)
                results.append({"file_id": filename_to_delete, "status": "success"})
            else:
                results.append({"file_id": filename_to_delete, "status": "not_found"})
        except Exception as e:
            results.append(
                {"file_id": filename_to_delete, "status": "error", "message": str(e)}
            )

    return jsonify({"results": results})


@app.route('/wishes', methods=['GET', 'POST'])
def handle_wishes():
    if request.method == 'POST':
        new_wish = request.json # 預期：{type, content}
        saved_wish = add_wish(new_wish)
    
        return jsonify(saved_wish)
        
    #logger.debug("準備寫入全域資料了!!")
    #logger.debug(json.dumps(wishes, ensure_ascii = False, indent = 4))
    wishes = get_wish_list()    
    return jsonify(wishes)


@app.route('/wishes/<int:wish_id>', methods=['DELETE'])
def delete_wish(wish_id):
    delete_wish_service(wish_id)
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=5000, debug = True, threaded = False) #單執行緒
    app.run(host="0.0.0.0", port=5000, debug = True, threaded = False) #單執行緒
