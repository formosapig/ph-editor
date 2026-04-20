# ph-editor/api/character_bp.py
import json
import logging
import os
import re
import shutil
from PIL import Image
from flask import Blueprint, Response, current_app, jsonify, request, send_file
from send2trash import send2trash
from core.shared_data import (
    add_or_update_character_with_path,
    
    get_character_data,
    get_character_file_entry,
    remove_character_file_entry,
    
    process_profile_data,
    process_scenario_data,
    process_tag_info,

    update_backstage_data,
    update_character_data,
    update_remark_data,
    update_status_data,

    get_suggest_file_id,
)
from core.user_config_manager import UserConfigManager
from utils.character_file_utils import reload_character_data
from utils.decorators import inject_character_file_entry, require_json_data, require_scan_path
from utils.exceptions import APIError, JSONError, NotFoundError, ValidationError
from utils.utils import sanitize_filename

logger = logging.getLogger(__name__)


api_characters_bp = Blueprint("api_characters", __name__, url_prefix="/api/characters")


@api_characters_bp.delete("")
@require_scan_path
def bulk_delete_characters(scan_path):
    """
    get sns from json object and remove then all. return success removed sns...
    """
    data = request.get_json()
    serial_numbers_to_delete = data.get("serial_numbers", [])  # 改為接收多個檔名（list）
    if not serial_numbers_to_delete or not isinstance(serial_numbers_to_delete, list):
        return jsonify({"status": "error", "message": "未提供檔案清單或格式錯誤"}), 400

    results = []
    for sn in serial_numbers_to_delete:
        entry = get_character_file_entry(sn)
        if not entry:
            results.append({"sn": sn, "status": "角色資料不存在"})
            continue

        full_path_original = os.path.join(scan_path, f"{entry.file_id}.png")
        logger.debug(f"Delete {full_path_original}")
        try:
            if os.path.exists(full_path_original):
                # os.remove(full_path_original) 太兇殘了.
                send2trash(full_path_original)
                logger.info(f"刪除原始檔案: {full_path_original}")
                remove_character_file_entry(sn)
                results.append({"sn": sn, "status": "success"})
            else:
                results.append({"sn": sn, "status": "file not found"})
        except Exception as e:
            results.append(
                {"sn": sn, "status": "error", "message": str(e)}
            )

    return jsonify({"results": results})


'''
@api_characters_bp.get("/<sn>/thumbnail")
@require_scan_path
def get_thumbnail(sn, scan_path):
    entry = get_character_file_entry(sn)
    if not entry:
        return f"Character with SN {sn} not found", 404
    
    file_path = os.path.join(scan_path, f"{entry.file_id}.png")
    if not os.path.exists(file_path):
        return f"File {entry.file_id}.png not found on disk", 404
    
    try:
        original_mtime = os.path.getmtime(file_path)
        
        with Image.open(file_path) as img:
            img = img.convert("RGB")
            img_io = io.BytesIO()
            img.save(img_io, 'JPEG', quality=85)
            img_io.seek(0)

        logger.debug(f"create thumbnail for {sn}")
        return send_file(
            img_io,
            mimetype='image/jpeg',
            as_attachment=False,
            download_name=f"{sn}.jpg",
            last_modified=original_mtime, # 關鍵：告訴瀏覽器這張圖的最後修改時間
        )

    except Exception as e:
        logger.error(f" [動態縮圖錯誤] {sn} 處理失敗: {e}")
        return "Internal Server Error", 500
'''


@api_characters_bp.get("/<sn>/thumbnail")
@require_scan_path
@inject_character_file_entry
def get_thumbnail(sn, entry, scan_path):
    # 原始檔案路徑
    file_path = os.path.join(scan_path, f"{entry.file_id}.png")
    if not os.path.exists(file_path):
        return NotFoundError(f"找不到原始檔案: {entry.file_id}.png")

    # 快取檔案路徑
    CACHE_DIR = UserConfigManager.get_cache_dir()
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    thumbnail_path = os.path.join(CACHE_DIR, f"{sn}.jpg")

    original_mtime = os.path.getmtime(file_path)
    
    # 檢查快取是否存在，且快取檔比原始檔「新」
    should_generate = True
    if os.path.exists(thumbnail_path):
        cache_mtime = os.path.getmtime(thumbnail_path)
        if cache_mtime >= original_mtime:
            should_generate = False

    if should_generate:
        logger.debug(f"Generating and saving thumbnail for {sn}")
        with Image.open(file_path) as img:
            img = img.convert("RGB")
            img.save(thumbnail_path, "JPEG", quality=85)
    else:
        pass

    # 從硬碟發送檔案
    return send_file(
        thumbnail_path,
        mimetype='image/jpeg',
        as_attachment=False,
        download_name=f"{sn}.jpg",
        last_modified=original_mtime
    )


@api_characters_bp.route("/reload", methods=["GET"])
def reload_file():
    file_id = request.args.get('file_id')
    if not file_id:
        return jsonify({'error': '缺少 file_id'}), 400
        
    try:
        scan_path = current_app.config["SCAN_PATH"]
        processed_result = reload_character_data(scan_path, file_id)

        # 如果是錯誤回傳（tuple）直接回應
        if isinstance(processed_result, tuple) and len(processed_result) == 2:
            return processed_result

        return Response(
            json.dumps(processed_result, ensure_ascii=False, indent=2),
            content_type="application/json",
        )

    except Exception as e:
        return jsonify({"error": f"內部錯誤: {e}"}), 500


@api_characters_bp.get("/<sn>/refresh")
@inject_character_file_entry
def refresh_character_data(entry):
    """
    刷新角色資料，讓前端能同步。
    """
    view_mode = request.args.get('view', 'gallery')

    if view_mode == 'gallery':        
        data = entry.to_dict(process_tag_info)
    else:
        raise ValidationError(f"不支援的視圖模式: {view_mode}", status_code=400)

    return jsonify(data)
    

@api_characters_bp.route("/save", methods=["POST"])
def save_file():
    """ 由前端傳來 fild_id 進行儲存 """
    data = request.get_json()
    file_id = data.get('file_id')
    
    if not file_id:
        return jsonify({'error': '缺少 file_id'}), 400

    entry = get_character_file_entry(file_id)
    if not entry:
        return (
            jsonify({"error": f"找不到角色資料：{file_id}，請重新載入檔案。"}),
            404,
        )

    try:
        entry.save(True)  # individual save only.
        return jsonify({"success": True, "message": "角色資料已成功保存！"})

    except FileNotFoundError as e:
        return jsonify({"error": f"檔案不存在：{str(e)}"}), 404
    except ValueError as e:
        return jsonify({"error": f"資料格式錯誤：{str(e)}"}), 400
    except IOError as e:
        return jsonify({"error": f"寫入檔案失敗：{str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"發生未知錯誤：{str(e)}"}), 500


@api_characters_bp.patch("/<sn>/data/<main_tab>/<sub_tab>")
@require_json_data
def patch_data(sn, main_tab, sub_tab, data):
    """
    更新當前角色 parsed_data 指定節點：
    URL 參數提供 sn， main_tab， sub_tab，
    JSON body 提供要更新的 data。
    """
    new_data = data.get("data")
    if new_data is None:
        raise JSONError("缺少 data 欄位。")

    # 新增：印出前端傳來的資料 json 字串到後端日誌
    #logger.debug(f"{sn} patch {main_tab}/{sub_tab} ：")
    #logger.debug("\n" + json.dumps(new_data, ensure_ascii = False, indent = 4))

    character_data_obj = get_character_data(sn)
    if not character_data_obj:
        raise NotFoundError(f"找不到角色資料: {sn}。請重新載入檔案。")

    if main_tab not in character_data_obj and main_tab != "story":
        raise KeyError(f"Invalid main_tab: '{main_tab}'.")

    need_update_profile_dropdown = False
    need_update_scenario_dropdown = False
    new_profile_id = None
    new_scenario_id = None
    need_save_all = False
        
    # 簡介資料檢查...
    if main_tab == "story" and sub_tab == "profile":
        success, new_profile_id = process_profile_data(sn, new_data)
        if not success:
            return jsonify(
                {
                    "success": False,
                    "message": f"角色資料節點 [{main_tab}][{sub_tab}] 不需要更新。",
                }
            )
        else:
            need_update_profile_dropdown = True

    # 場景資料檢查...
    if main_tab == "story" and sub_tab == "scenario":
        success, new_scenario_id = process_scenario_data(sn, new_data)
        if not success:
            return jsonify(
                {
                    "success": False,
                    "message": f"角色資料節點 [{main_tab}][{sub_tab}] 不需要更新。",
                }
            )
        else:
            need_update_scenario_dropdown = True

    # 幕後資料檢查
    if main_tab == "story" and sub_tab == "backstage":
        success = update_backstage_data(sn, new_data)
        if not success:
            return jsonify(
                {
                    "success": False,
                    "message": f"角色資料節點 [{main_tab}][{sub_tab}] 不需要更新。",
                }
            )

    # 新增：印出前端傳來的資料 json 字串到後端日誌
    #logger.debug("結果：")
    #logger.debug(json.dumps(new_data, ensure_ascii = False, indent = 2))

    # 更新子節點
    if main_tab != "story":
        update_character_data(sn, main_tab, sub_tab, new_data)

    response_data = {
        "success": True,
        "message": f"角色資料節點 [{main_tab}][{sub_tab}] 更新成功（尚未寫入檔案）。",
    }

    # 加入額外標記
    if need_update_profile_dropdown:
        response_data["need_update_profile_dropdown"] = True
    if need_update_scenario_dropdown:
        response_data["need_update_scenario_dropdown"] = True        
    if new_profile_id is not None:
        response_data["new_profile_id"] = new_profile_id
    if new_scenario_id is not None:
        response_data["new_scenario_id"] = new_scenario_id        

    return jsonify(response_data)


@api_characters_bp.patch("/<sn>/remark")
@require_json_data
def patch_character_remark(sn, data):
    """ 更新角色的備註 """
    remark = data.get("remark")
    if remark is None:
        return jsonify({"error": "缺少 remark 。"}), 400

    success = update_remark_data(sn, remark)
    
    if not success:
        return jsonify(
            {
                "success": False,
                "message": f"更新角色 {sn} 備註 {remark} 失敗。",
            }
        )
    
    return jsonify({
        "success": True,
        "message": f"更新角色註解(REMARK)成功。",
    })


@api_characters_bp.patch("/<sn>/status")
@require_json_data
def patch_status(sn, data):
    """ 更新角色的狀態 """
    new_status = data.get('status')
    if not new_status:
        return jsonify({"error": "缺少 status 。"}), 400

    update_status_data(sn, new_status)
    
    return jsonify({
        "success": True,
        "message": f"更新檔案狀態(STATUS)成功。",
    })


@api_characters_bp.get("/<sn>/suggest")
def get_suggest(sn):
    """ 取得建議的 file_id ，任何失敗都回傳 未知 """
    suggest = get_suggest_file_id(sn)

    return jsonify({"success": True, "suggested": suggest})


@api_characters_bp.patch("/<sn>/rename")
@require_scan_path
@require_json_data
@inject_character_file_entry
def patch_rename(sn, entry, data, scan_path):
    """
    對 sn 指定的檔案進行更改 file_id 的動作，包含 metadata 及 os 層的檔案名稱更改
    """
    old_file_id = entry.file_id
    new_file_id = data.get("new_file_id")
    if not old_file_id or not new_file_id:
        raise ValidationError("缺少新/舊檔名。")

    old_path_full = os.path.join(scan_path, f"{old_file_id}.png")
    new_path_full = os.path.join(scan_path, f"{new_file_id}.png")

    logger.debug(f"{old_path_full} -> {new_path_full}")

    if not old_path_full.startswith(scan_path) or not new_path_full.startswith(scan_path):
        return jsonify({"success": False, "error": "不允許的操作：路徑超出掃描目錄範圍"}), 403

    if not os.path.isfile(old_path_full):
        raise NotFoundError(f"{old_path_full} 不存在。")

    if os.path.exists(new_path_full):
        raise FileExistsError(f"目標檔案已存在: {new_file_id}")
    
    try:
        os.rename(old_path_full, new_path_full)
        logger.info(f"成功重新命名：{old_path_full} -> {new_path_full}")
    except OSError as e:
        # 重點：在這裡攔截作業系統錯誤，並拋出你已經有 Handler 處理的 APIError
        # e.errno 123 在 Windows 就是檔名語法錯誤
        logger.error(f"Rename failed: {str(e)}")
        raise ValidationError(f"作業系統拒絕改名：{e.strerror} (請檢查檔名是否包含非法字元)")
    except Exception as e:
        # 其他可能的權限錯誤
        raise APIError(f"重新命名失敗：{str(e)}", status_code=500)
        
    entry.change_file_id(new_file_id)
    return jsonify({"success": True})


@api_characters_bp.post("/<sn>/clone")
@require_scan_path
@inject_character_file_entry
def copy_clone(scan_path, entry):
    file_id = entry.file_id
    if not file_id:
        raise ValidationError("缺少 file_id 。")

    # 核心邏輯：若結尾有 (n)，數字+1；否則加 (1)
    match = re.search(r"\((\d+)\)$", file_id)
    if match:
        new_id = re.sub(r"\((\d+)\)$", f"({int(match.group(1)) + 1})", file_id)
    else:
        new_id = f"{file_id}(1)"
    
    src = os.path.join(scan_path, f"{file_id}.png")
    dest = os.path.join(scan_path, f"{new_id}.png")
    
    shutil.copy2(src, dest)
    new_entry = add_or_update_character_with_path(scan_path, new_id)
    new_entry.to_dict()
    return jsonify({"new_data": new_entry.to_dict()})