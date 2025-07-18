from flask import Flask, request, jsonify, send_from_directory, render_template
from PIL import Image
from flask import current_app
import os
import time
import logging
from web.edit_bp import edit_bp
from web.general_bp import general_bp
from api.character import api_character_bp
from api.profile import api_profile_bp
from api.ui_config import api_ui_config_bp

# 從 shared_data 模組引入相關函式
from core.shared_data import (
    characters_db,
    add_or_update_character_with_path,
    clear_characters_db,
    get_all_character_ids,
    get_profile_name,
)
from core.user_config_manager import UserConfigManager

# 初始化時確保所有目錄存在
UserConfigManager.ensure_dir()

app = Flask(__name__)
app.register_blueprint(edit_bp)
app.register_blueprint(general_bp)
app.register_blueprint(api_character_bp)
app.register_blueprint(api_profile_bp)
app.register_blueprint(api_ui_config_bp)

# 設定快取路徑
CACHE_DIR = UserConfigManager.get_cache_dir()
# 設定掃描路徑
scan_path = UserConfigManager.load_scan_path()
app.config['SCAN_PATH'] = scan_path if scan_path else ""
# 設定 session key
app.config['SECRET_KEY'] = 'sadflkfsdflksdf' # 替換這裡

# 獲取 Werkzeug 的日誌器
log = logging.getLogger('werkzeug')
# 將 Werkzeug 的日誌級別設定為 WARNING 或 ERROR
# WARNING 會顯示警告和錯誤，ERROR 只顯示錯誤
# 304 訊息屬於 INFO 級別，所以設定為 WARNING 或 ERROR 就不會顯示了
log.setLevel(logging.WARNING) # 或者 logging.ERROR

def clean_old_thumbnails(cache_dir, max_remove=3):
    if not os.path.exists(cache_dir):
        return
    files = [
        (f, os.path.getmtime(os.path.join(cache_dir, f)))
        for f in os.listdir(cache_dir)
        if f.lower().endswith(('.png', '.jpg'))
    ]
    files.sort(key=lambda x: x[1])  # sort by oldest
    for f, _ in files[:max_remove]:
        try:
            os.remove(os.path.join(cache_dir, f))
            #print(f"刪除快取縮圖: {f}")
        except Exception as e:
            print(f"刪除失敗: {f}, {e}")

clean_old_thumbnails(CACHE_DIR) # 應用啟動時執行清理

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cache/<path:filename>')
def serve_cache(filename):
    return send_from_directory(CACHE_DIR, filename)

@app.route('/get_scan_path', methods=['GET'])
def get_scan_path():
    path = UserConfigManager.load_scan_path()
    return jsonify({'scanPath': path or ''})
    
@app.route('/scan', methods=['POST'])
def scan_folder():
    folder_path = request.json.get('path')

    if not folder_path:
        return jsonify({'error': '缺少資料夾路徑'}), 400
    
    if not os.path.isdir(folder_path):
        return jsonify({'error': '無效的資料夾路徑'}), 400

    app.config['SCAN_PATH'] = folder_path # 更新應用程式配置中的掃描路徑
    UserConfigManager.save_scan_path(folder_path)  # ✅ 改用此處理

    # 清空現有的數據庫，以便重新掃描
    clear_characters_db() 
    
    thumbnails = [] # 儲存生成或更新的縮圖檔案名
    loaded_character_count = 0
    character_list = [] # 儲存 thumbnail, character_id, profile_name

    print(f"開始掃描資料夾 '{folder_path}'...")
    for root, _, files in os.walk(folder_path):
        for file_name_with_ext in files:
            if file_name_with_ext.lower().endswith('.png'):
                file_path = os.path.join(root, file_name_with_ext)
                character_id = os.path.splitext(file_name_with_ext)[0] 
                
                # --- 縮圖生成邏輯 ---
                thumbnail_name = f"thumb_{character_id}.jpg"
                thumbnail_path = os.path.join(CACHE_DIR, thumbnail_name)
                
                try:
                    original_mtime = os.path.getmtime(file_path)
                    if os.path.exists(thumbnail_path):
                        cache_mtime = os.path.getmtime(thumbnail_path)
                        if original_mtime <= cache_mtime:
                            thumbnails.append(thumbnail_name)
                            # print(f"  [縮圖] 快取未過期，跳過: {file_name_with_ext}")
                            pass # 不跳過，因為還要處理角色數據
                except Exception as e:
                    print(f"  [縮圖] 處理 '{file_name_with_ext}' 縮圖快取時發生錯誤: {e}")
                    # 不阻礙後續的 CharacterData 載入，但會嘗試重新生成縮圖

                # 嘗試生成/更新縮圖
                try:
                    # 如果縮圖不存在或已過期，則重新生成
                    if not os.path.exists(thumbnail_path) or original_mtime > os.path.getmtime(thumbnail_path):
                        with Image.open(file_path) as img:
                            img = img.convert("RGB")
                            # img.thumbnail((189, 264)) # 等比縮圖，寬不超過189，高不超過264
                            img.save(thumbnail_path, format='JPEG', quality=70)
                        # print(f"  [縮圖] 生成/更新縮圖: {file_name_with_ext}")
                    
                    #if thumbnail_name not in thumbnails: # 避免重複添加，如果之前快取判斷沒有跳過
                    #    thumbnails.append(thumbnail_name)

                except Exception as e:
                    print(f"  [錯誤] 生成縮圖 '{file_name_with_ext}' 失敗: {e}")
                    # 縮圖失敗不影響角色數據載入，繼續
                # --- 縮圖生成邏輯結束 ---


                # --- 角色數據載入邏輯 ---
                try:
                    add_or_update_character_with_path(folder_path, character_id)
                    loaded_character_count += 1
                except Exception as e:
                    print(f"  [錯誤] 載入或解析檔案 '{file_name_with_ext}' 的角色數據時發生錯誤: {e}")
                    continue # 繼續處理下一個檔案
            
                # 將資料整理好放進 character_list
                print(f"prepare get profile name {character_id}")
                profile_name = get_profile_name(character_id)
                character_list.append({
                    'thumb': thumbnail_name,
                    'id': character_id,
                    'profile_name': profile_name or '' # 若無資料則為空字串
                })
    
    print(f"掃描完成。總計處理 {len(thumbnails)} 個檔案，成功載入 {loaded_character_count} 個角色數據。")
    return jsonify({'images': character_list, 'message': f"成功掃描 {len(thumbnails)} 個檔案並載入 {loaded_character_count} 個角色數據。"})

@app.route('/rename', methods=['POST'])
def rename():
    data = request.get_json()
    old_path = data.get('old_name')
    new_path = data.get('new_name')

    if not old_path or not new_path:
        return jsonify({"success": False, "error": "缺少舊檔名或新檔名"}), 400

    if not os.path.isfile(old_path):
        return jsonify({"success": False, "error": "舊檔案不存在"}), 400

    try:
        os.rename(old_path, new_path)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
        
@app.route('/delete_files', methods=['POST'])
def delete_files():
    data = request.get_json()
    filenames_to_delete = data.get('filenames')  # 改為接收多個檔名（list）

    if not filenames_to_delete or not isinstance(filenames_to_delete, list):
        return jsonify({'status': 'error', 'message': '未提供檔案清單或格式錯誤'}), 400

    scan_path = UserConfigManager.load_scan_path()
    if not scan_path:
        return jsonify({'status': 'error', 'message': '請先掃描一個資料夾'}), 400

    results = []
    for filename_to_delete in filenames_to_delete:
        full_path_original = os.path.join(scan_path, filename_to_delete)
        try:
            if os.path.exists(full_path_original):
                os.remove(full_path_original)
                print(f"刪除原始檔案: {full_path_original}")
                results.append({'filename': filename_to_delete, 'status': 'success'})
            else:
                results.append({'filename': filename_to_delete, 'status': 'not_found'})
        except Exception as e:
            results.append({'filename': filename_to_delete, 'status': 'error', 'message': str(e)})

    return jsonify({'results': results})
        
if __name__ == '__main__':
    app.run(debug=True, threaded=True)