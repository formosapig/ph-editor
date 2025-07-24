# ph-editor/api/character.py
import json
import logging
from typing import Any, Dict, Tuple, Union
from flask import Blueprint, Response, current_app, jsonify, request, session
from core.character_file_entry import CharacterFileEntry
from core.shared_data import (
    add_or_update_character_with_path,
    add_profile,
    add_scenario,
    characters_db,
    characters_db_lock,
    get_character_data,
    get_character_file_entry,
    get_global_general_data,
    get_profile,
    get_scenario,
    update_global_general_data,
    update_profile,
    update_scenario,
)

logger = logging.getLogger(__name__)

api_character_bp = Blueprint("api_character", __name__, url_prefix="/api/character")


def ensure_general_data_updated(character_entry: CharacterFileEntry) -> None:
    character_data = character_entry.get_character_data()
    global_general = get_global_general_data()
    global_version = global_general.get("!version", -1)

    character_general = character_data.get_value(["story", "general"])
    character_version = (
        character_general.get("!version", -1)
        if isinstance(character_general, dict)
        else -1
    )

    if not isinstance(character_general, dict) or character_version < global_version:
        data = character_data.get_data()
        if "story" not in data:
            data["story"] = {}

        data["story"]["general"] = global_general
        character_data.global_data = global_general
        character_entry.general_version = global_version
        character_entry.set_sync_flag(True)


def ensure_profile_data_updated(character_entry: CharacterFileEntry) -> None:
    if character_entry.profile_id is None:
        return

    global_profile_data = get_profile(character_entry.profile_id)
    global_profile_version = global_profile_data.get("!version", -1)

    character_data = character_entry.get_character_data()
    character_profile_data = character_data.get_value(["story", "profile"])
    character_profile_version = character_entry.profile_version

    if (
        not isinstance(character_profile_data, dict)
        or character_profile_version < global_profile_version
    ):
        data = character_data.get_data()

        # 確保 "story" 存在
        if "story" not in data:
            data["story"] = {}

        # 直接更新 profile 區塊（不透過 set_value）
        data["story"]["profile"] = global_profile_data.copy()

        # 更新 character_entry 的 profile 狀態
        character_entry.profile_id = global_profile_data.get(
            "!id", character_entry.profile_id
        )
        character_entry.profile_version = global_profile_version

        character_entry.set_sync_flag(True)


def ensure_scenario_data_updated(character_entry: CharacterFileEntry) -> None:
    if character_entry.scenario_id is None:
        return

    global_scenario_data = get_scenario(character_entry.scenario_id)
    global_scenario_version = global_scenario_data.get("!version", -1)

    character_data = character_entry.get_character_data()
    character_scenario_data = character_data.get_value(["story", "scenario"])
    character_scenario_version = character_entry.scenario_version

    if (
        not isinstance(character_scenario_data, dict)
        or character_scenario_version < global_scenario_version
    ):
        data = character_data.get_data()

        # 確保 "story" 存在
        if "story" not in data:
            data["story"] = {}

        # 直接更新 profile 區塊（不透過 set_value）
        data["story"]["scenario"] = global_scenario_data.copy()

        # 更新 character_entry 的 scenario 狀態
        character_entry.scenario_id = global_scenario_data.get(
            "!id", character_entry.scenario_id
        )
        character_entry.scenario_version = global_scenario_version

        character_entry.set_sync_flag(True)


def reload_character_data(
    scan_path: str, file_id: str
) -> Union[Dict[str, Any], Tuple]:
    """
    重新讀取角色圖檔並解析，更新共享資料庫，並確保 general 資料是最新。
    成功回傳 character_data.get_data()。
    發生錯誤時回傳 (jsonify響應, status_code) tuple。
    """
    try:
        add_or_update_character_with_path(scan_path, file_id)

        character_file_entry_obj = get_character_file_entry(file_id)
        if not character_file_entry_obj:
            return (
                jsonify(
                    {
                        "error": f"雖然成功讀取檔案，但解析後仍無法取得角色數據: {file_id}。"
                    }
                ),
                500,
            )

        ensure_general_data_updated(character_file_entry_obj)
        ensure_profile_data_updated(character_file_entry_obj)
        ensure_scenario_data_updated(character_file_entry_obj)

        character_data_obj = character_file_entry_obj.get_character_data()
        return character_data_obj.get_data()

    except FileNotFoundError:
        return jsonify({"error": "檔案不存在。", "parsed_data_preview": "無"}), 404
    except Exception as e:
        return jsonify({"error": f"讀取角色檔案時發生錯誤: {e}"}), 500


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
    """
    從 session 拿 file_id，呼叫 CharacterFileEntry.save() 來存檔。
    處理並回傳各類異常訊息。
    """
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
        return jsonify({"error": f"發生未知錯誤: {str(e)}"}), 500


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
        # 若 main_tab 不存在，建立空 dict
        if main_tab not in character_data_obj.parsed_data:
            character_data_obj.parsed_data[main_tab] = {}

        need_update_profile_dropdown = False
        need_update_scenario_dropdown = False
        new_profile_id = None
        new_scenario_id = None
        need_save_all = False

        # 簡介資料檢查...
        if main_tab == "story" and sub_tab == "profile":
            profile_id = new_data.get("!id")
            if profile_id == 0:
                success = add_profile(file_id, new_data)
                new_profile_id = new_data.get("!id", None)
            else:
                success = update_profile(file_id, new_data)
                # 更新時, 不參考前端的 !version , new_data 也不會更新 !version

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
            scenario_id = new_data.get("!id")
            if scenario_id == 0:
                success = add_scenario(file_id, new_data)
                new_scenario_id = new_data.get("!id", None)
            else:
                success = update_scenario(file_id, new_data)
                # 更新時, 不參考前端的 !version , new_data 也不會更新 !version

            if not success:
                return jsonify(
                    {
                        "success": False,
                        "message": f"角色資料節點 [{main_tab}][{sub_tab}] 不需要更新。",
                    }
                )
            else:
                need_update_scenario_dropdown = True

        # 新增：印出前端傳來的資料 json 字串到後端日誌
        logger.debug("結果：")
        logger.debug(json.dumps(new_data, ensure_ascii=False, indent=2))

        # 更新子節點
        character_data_obj.parsed_data[main_tab][sub_tab] = new_data

        response_data = {
            "success": True,
            "message": f"角色資料節點 [{main_tab}][{sub_tab}] 更新成功（尚未寫入檔案）。",
        }

        # 全域資料檢查...
        if main_tab == "story" and sub_tab == "general":
            update_global_general_data(new_data, increment_version=True)
            need_save_all = True

        # 加入額外標記
        if need_update_profile_dropdown:
            response_data["need_update_profile_dropdown"] = True
        if need_update_scenario_dropdown:
            response_data["need_update_scenario_dropdown"] = True        
        if new_profile_id is not None:
            response_data["new_profile_id"] = new_profile_id
        if new_scenario_id is not None:
            response_data["new_scenario_id"] = new_scenario_id        
        if need_save_all:
            response_data["need_save_all"] = True

        # 若節點不是 'story' 'general' 或 'story' 'profile' 或 'story' 'scenario' 時，把 save_flag 設為 true
        entry = get_character_file_entry(file_id)
        if entry is not None:
            # 順便更新一下 tag_id
            if main_tab == "story" and sub_tab == "backstage":
                entry.update_tag_id()

            if not (main_tab == "story" and sub_tab in ("general", "profile", "scenario")):
                entry.set_save_flag(True)
                response_data["need_save"] = True

            # 看一下 save flag
            #logger.debug(f"save flag : {entry.save_flag}")
        else:
            logger.warning(
                f"Character file entry not found for file_id: {file_id}"
            )

        return jsonify(response_data)

    except Exception as e:
        import traceback

        traceback.print_exc()  # 會印出錯誤堆疊
        return jsonify({"error": f"更新失敗: {str(e)}"}), 500
