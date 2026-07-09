# ph-editor/api/character_bp.py
import logging
import os
import re
import shutil
from PIL import Image
from flask import Blueprint, jsonify, request, send_file
from core.shared_data import (
    add_or_update_character_with_path,
    
    get_character_data,
    process_profile_data,
    process_scenario_data,
    process_tag_info,

    update_backstage_data,
    update_character_data,
    update_remark_data,
    get_suggest_file_id,
)
from core.user_config_manager import UserConfigManager
from utils.decorators import inject_character_file_entry, require_json_data, require_scan_path
from utils.exceptions import APIError, JSONError, NotFoundError, ValidationError

logger = logging.getLogger(__name__)


api_character_bp = Blueprint("api_character", __name__, url_prefix="/api/character")


@api_character_bp.get("/<sn>/thumbnail")
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


@api_character_bp.get("/<sn>/refresh")
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
    

@api_character_bp.patch("/<sn>/data/<main_tab>/<sub_tab>")
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
        "message": f"角色資料節點 [{main_tab}][{sub_tab}] 更新成功。",
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


@api_character_bp.patch("/<sn>/remark")
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


@api_character_bp.get("/<sn>/suggest")
def get_suggest(sn):
    """ 取得建議的 file_id ，任何失敗都回傳 未知 """
    is_success, suggest = get_suggest_file_id(sn)

    return jsonify({"success": is_success, "suggested": suggest})


@api_character_bp.patch("/<sn>/rename")
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

    #logger.debug(f"{old_path_full} -> {new_path_full}")

    if not old_path_full.startswith(scan_path) or not new_path_full.startswith(scan_path):
        return jsonify({"success": False, "error": "不允許的操作：路徑超出掃描目錄範圍"}), 403

    if not os.path.isfile(old_path_full):
        raise NotFoundError(f"{old_path_full} 不存在。")

    if os.path.exists(new_path_full):
        raise FileExistsError(f"目標檔案已存在: {new_file_id}")
    
    try:
        os.rename(old_path_full, new_path_full)
        #logger.info(f"成功重新命名：{old_path_full} -> {new_path_full}")
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


@api_character_bp.post("/<sn>/clone")
@require_scan_path
@inject_character_file_entry
def post_clone(scan_path, entry):
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
    new_entry.clone_from(entry)
    new_entry.to_dict()
    return jsonify({"new_data": new_entry.to_dict()})

@api_character_bp.patch("/<sn>/upstream/<upstream_sn>")
@inject_character_file_entry
def patch_character_upstream(entry, upstream_sn):

    # ROOT = most upstream
    # "" = no upstream
    # 目前似乎不會失敗？
    success = entry.update_upstream_sn(upstream_sn);

    if not success:
        return jsonify(
            {
                "success": False,
                "message": f"更新角色 {entry.sn} 溯源備註 {upstream_sn} 失敗。",
            }
        )
    
    return jsonify({
        "success": True,
        "message": f"更新角色溯源 (UPSTREAM_SN) 成功。",
    })