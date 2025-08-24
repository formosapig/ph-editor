# ph-editor/api/character.py
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
    get_profile,
    get_scenario,
    
    process_profile_data,
    process_scenario_data,
    update_backstage_data,
    update_character_data,
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


'''
@api_character_bp.route("/ping_pong_sync", methods=["POST"])
def ping_pong_sync():
    """
    掃描 characters_db 找第一個 sync_flag 為 True 的角色，呼叫其 save() 儲存。
    回傳成功或錯誤 JSON。
    """
    saved_file_id: str | None = None

    try:
        with characters_db_lock:
            for file_id, character_file_entry in characters_db.items():
                if character_file_entry.needs_syncing():
                    character_file_entry.save()
                    # character_file_entry.set_sync_flag(False) 上一行的 save 內會做.
                    saved_file_id = file_id
                    break

        if saved_file_id:
            return (
                jsonify(
                    {
                        "success": True,
                        "message": f"成功儲存角色: {saved_file_id}",
                        "file_id": saved_file_id,
                    }
                ),
                200,
            )
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "沒有找到待儲存的角色。",
                        "file_id": None,
                    }
                ),
                200,
            )

    except FileNotFoundError as e:
        return jsonify({"error": f"檔案不存在: {str(e)}"}), 404
    except ValueError as e:
        return jsonify({"error": f"資料格式錯誤: {str(e)}"}), 400
    except IOError as e:
        return jsonify({"error": f"寫入檔案失敗: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"發生未知錯誤: {str(e)}"}), 500'''


@api_character_bp.route("/update/<main_tab>/<sub_tab>", methods=["PUT"])
def update_data(main_tab, sub_tab):
    """
    更新當前角色 parsed_data 指定節點：
    URL 參數提供 main_tab 和 sub_tab，
    JSON body 提供要更新的 data。
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "請求內容必須是 JSON 格式。"}), 400

    new_data = data.get("data")
    if new_data is None:
        return jsonify({"error": "缺少 data 欄位。"}), 400

    file_id = data.get("file_id")
    if not file_id:
        return jsonify({'error': '缺少 file_id'}), 400

    # 新增：印出前端傳來的資料 json 字串到後端日誌
    logger.debug(f"{file_id} update {main_tab}/{sub_tab} ：")
    logger.debug("\n" + json.dumps(new_data, ensure_ascii=False, indent=2))

    character_data_obj = get_character_data(file_id)
    if not character_data_obj:
        return (
            jsonify({"error": f"找不到角色數據: {file_id}。請重新載入檔案。"}),
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

        # 全域資料檢查...
        if main_tab == "story" and sub_tab == "general":
            update_general_data(new_data)
            
        # 簡介資料檢查...
        if main_tab == "story" and sub_tab == "profile":
            success, new_profile_id = process_profile_data(file_id, new_data)

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
            success, new_scenario_id = process_scenario_data(file_id, new_data)

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
            success = update_backstage_data(file_id, new_data)

            if not success:
                return jsonify(
                    {
                        "success": False,
                        "message": f"角色資料節點 [{main_tab}][{sub_tab}] 不需要更新。",
                    }
                )

        # 新增：印出前端傳來的資料 json 字串到後端日誌
        logger.debug("結果：")
        logger.debug(json.dumps(new_data, ensure_ascii=False, indent=2))

        # 更新子節點
        if main_tab != "story":
            update_character_data(file_id, main_tab, sub_tab, new_data)

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

        # 若節點不是 'story' 'general' 或 'story' 'profile' 或 'story' 'scenario' 時，把 save_flag 設為 true
        #entry = get_character_file_entry(file_id)
        #if entry is not None:
            # 順便更新一下 tag_id
        #    if main_tab == "story" and sub_tab == "backstage":
        #        entry.update_tag_id()

        #    if not (main_tab == "story" and sub_tab in ("general", "profile", "scenario")):
        #        entry.set_save_flag(True)
        #        response_data["need_save"] = True

            # 看一下 save flag
            #logger.debug(f"save flag : {entry.save_flag}")
        #else:
        #    logger.warning(
        #        f"Character file entry not found for file_id: {file_id}"
        #    )

        return jsonify(response_data)

    except Exception as e:
        import traceback

        traceback.print_exc()  # 會印出錯誤堆疊
        return jsonify({"error": f"更新失敗: {str(e)}"}), 500
