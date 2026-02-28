# ph-editor/api/character_bp.py
import json
import logging
from typing import Any, Dict, Tuple, Union
from flask import Blueprint, Response, current_app, jsonify, request, session
from core.character_file_entry import CharacterFileEntry
from core.shared_data import (
    add_or_update_character_with_path,
    
    characters_db,
    get_character_data,
    get_character_file_entry,
    
    process_profile_data,
    process_scenario_data,
    process_tag_info,
    update_backstage_data,
    update_character_data,
    update_remark_data,
    update_status_data,

    get_suggest_file_id,
)
from utils.character_file_utils import reload_character_data


logger = logging.getLogger(__name__)


api_character_bp = Blueprint("api_character", __name__, url_prefix="/api/character")


@api_character_bp.route("/reload", methods=["GET"])
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


@api_character_bp.get("/<sn>/refresh")
def refresh_character_data(sn):
    """
    刷新角色資料，讓前端能同步。
    """
    try:
        entry = get_character_file_entry(sn)
        if not entry:
            logger.warning(f"刷新角色 '{sn}' 失敗。")
            return jsonify({"error": "找不到指定的角色"}), 404
        
        view_mode = request.args.get('view', 'gallery')
        
        tag_style, tag_name = process_tag_info(sn)

        if view_mode == 'gallery':        

            data = {
                "sn": entry.sn,
                "file_id": entry.file_id,
                "thumb": f"thumb_{entry.file_id}.jpg",
                "profile_name": entry.get_profile_name(),
                "scenario_title": entry.get_scenario_title(),
                "remark": entry.get_remark(),
                "status": entry.get_status(),
                "tag_style": tag_style,
                "tag_name": tag_name
            }

        else:
            return jsonify({"error": f"不支援的視圖模式: {view_mode}"}), 400

        return jsonify(data)

    except Exception as e:
        logger.exception(f"處理檔案 '{sn}' 時發生內部錯誤。")
        return jsonify({"error": f"處理檔案時發生內部錯誤: {str(e)}"}), 500
    

@api_character_bp.route("/save", methods=["POST"])
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


@api_character_bp.patch("/<sn>/data/<main_tab>/<sub_tab>")
def patch_data(sn, main_tab, sub_tab):
    """
    更新當前角色 parsed_data 指定節點：
    URL 參數提供 sn， main_tab， sub_tab，
    JSON body 提供要更新的 data。
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "請求內容必須是 JSON 格式。"}), 400

    new_data = data.get("data")
    if new_data is None:
        return jsonify({"error": "缺少 data 欄位。"}), 400

    # 新增：印出前端傳來的資料 json 字串到後端日誌
    logger.debug(f"{sn} patch {main_tab}/{sub_tab} ：")
    logger.debug("\n" + json.dumps(new_data, ensure_ascii = False, indent = 4))

    character_data_obj = get_character_data(sn)
    if not character_data_obj:
        return (
            jsonify({"error": f"找不到角色數據: {sn}。請重新載入檔案。"}),
            404,
        )

    try:
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
        logger.debug("結果：")
        logger.debug(json.dumps(new_data, ensure_ascii = False, indent = 2))

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

    except Exception as e:
        import traceback

        traceback.print_exc()  # 會印出錯誤堆疊
        return jsonify({"error": f"更新失敗: {str(e)}"}), 500


@api_character_bp.patch("/<sn>/remark")
def patch_character_remark(sn):
    """ 更新角色的備註 """
    data = request.get_json()
    if not data:
        return jsonify({"error": "請求內容必須是 JSON 格式。"}), 400
    remark = data.get("remark")
    if remark is None:
        return jsonify({"error": "缺少 remark 。"}), 400

    try:
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
            
    except Exception as e:
        logger.error(e)
        return jsonify({"error": f"更新失敗: {str(e)}"}), 500

    
@api_character_bp.patch("/<sn>/status")
def patch_character_status(sn):
    """ 更新角色的狀態 """
    data = request.get_json()
    if not data:
        return jsonify({"error": "請求內容必須是 JSON 格式。"}), 400
    new_status = data.get('status')
    if not new_status:
        return jsonify({"error": "缺少 status 。"}), 400

    try:
        update_status_data(sn, new_status)
        
        return jsonify({
            "success": True,
            "message": f"更新檔案狀態(STATUS)成功。",
        })
            
    except Exception as e:
        logger.error(e)
        return jsonify({"error": f"更新失敗: {str(e)}"}), 500


@api_character_bp.get("/<sn>/suggest")
def get_suggest(sn):
    """ 取得建議的 file_id ，任何失敗都回傳 未知 """
    suggest = get_suggest_file_id(sn)

    return jsonify({"success": True, "suggested": suggest})


@api_character_bp.patch("/<sn>/rename")
def patch_rename(sn):
    """
    對 sn 指定的檔案進行更改 file_id 的動作，包含 metadata 及 os 層的檔案名稱更改
    """
    """
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "請求的 JSON 資料無效"}), 400

    # 1. 取得並檢查必要的參數
    old_name = data.get("old_filename")
    new_name = data.get("new_filename")

    if not old_name or not new_name:
        return jsonify({"success": False, "error": "缺少舊檔名或新檔名"}), 400

    # 2. 取得掃描路徑並安全地組合完整路徑
    if not scan_path:
        return jsonify({"success": False, "error": "掃描路徑未設定"}), 500

    # 使用 os.path.join 組合路徑，避免路徑拼接錯誤
    old_path_full = os.path.join(scan_path, f"{old_name}.png")
    new_path_full = os.path.join(scan_path, f"{new_name}.png")


    快取檔案也要更改....

    logger.debug(f"{old_path_full} -> {new_path_full}")

    # 3. 增加安全性檢查，防止路徑遍歷攻擊
    # 確保新舊路徑都在掃描目錄下
    if not old_path_full.startswith(scan_path) or not new_path_full.startswith(scan_path):
        return jsonify({"success": False, "error": "不允許的操作：路徑超出掃描目錄範圍"}), 403

    # 4. 進行檔案存在性檢查
    if not os.path.isfile(old_path_full):
        # 紀錄錯誤訊息，以便偵錯
        logger.error(f"檔案不存在：{old_path_full}")
        return jsonify({"success": False, "error": "舊檔案不存在"}), 404

    # 5. 執行重新命名操作並處理潛在錯誤
    try:
        # 檢查新檔名是否已存在，避免覆蓋
        if os.path.exists(new_path_full):
             raise FileExistsError(f"目標檔案已存在: {new_name}")

        os.rename(old_path_full, new_path_full)
        logger.info(f"成功重新命名：{old_path_full} -> {new_path_full}")
        
        # 6. 成功更名後，修改記憶體及常駐資料...
        file_entry = get_character_file_entry(old_name)
        if not file_entry:
            # 【關鍵改動】如果記憶體更新失敗，手動觸發回滾
            logger.error(f"記憶體缺失，正在回滾檔案名稱: {new_name} -> {old_name}")
            os.rename(new_path_full, old_path_full) # 改回來
            raise ValueError(f"找不到對應的 File Entry : {old_name}")
            
        file_entry.change_filename(new_name)    
        
        return jsonify({"success": True})
    except FileExistsError:
        # 如果新檔名已存在
        logger.error(f"重新命名失敗：新檔案已存在：{new_path_full}")
        return jsonify({"success": False, "error": "新檔名已存在"}), 409
    except ValueError as e:
        # 【標註：改動點】專門捕捉找不到 file_entry 的錯誤
        logger.error(f"資料一致性錯誤：{e}")
        return jsonify({"success": False, "error": str(e)}), 404
    except Exception as e:
        # 捕捉其他可能的錯誤，例如權限問題等
        logger.error(f"重新命名時發生錯誤：{e}")
        return jsonify({"success": False, "error": f"重新命名失敗：{str(e)}"}), 500
"""