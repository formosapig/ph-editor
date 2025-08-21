# ph-editor/web/edit_bp.py
import json
import logging
from typing import Any, Dict
from flask import (
    Blueprint,
    current_app,
    jsonify,
    render_template,
    request,
    session,
)

from core.character_file_entry import CharacterFileEntry
# get_character_data 會處理延遲解析邏輯
from core.shared_data import (
    add_or_update_character_with_path,
    get_character_file_entry,
    get_general_data,
    
    get_profile,
    get_scenario,
)
from utils.character_file_utils import (
    reload_character_data,
    append_general_data,
)

edit_bp = Blueprint("edit_bp", __name__)


logger = logging.getLogger(__name__)
#logger.disabled = True


"""def ensure_profile_data_updated(character_entry: CharacterFileEntry) -> None:
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

        character_entry.set_sync_flag(True)"""


"""def ensure_scenario_data_updated(character_entry: CharacterFileEntry) -> None:
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

        character_entry.set_sync_flag(True)"""
        
        
"""def reload_character_data(scan_path: str, file_id: str) -> [Dict[str, Any], tuple]:
    
    #重新讀取角色圖檔並解析，更新共享資料庫，並確保 general 資料是最新。
    #成功回傳 character_data.get_data()。
    #發生錯誤時回傳 (jsonify響應, status_code) tuple。
    
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

        ensure_profile_data_updated(character_file_entry_obj)
        ensure_scenario_data_updated(character_file_entry_obj)

        character_data_obj = character_file_entry_obj.get_character_data()
        return character_data_obj.get_data()

    except FileNotFoundError:
        return jsonify({"error": "檔案不存在。", "parsed_data_preview": "無"}), 404
    except Exception as e:
        return jsonify({"error": f"讀取角色檔案時發生錯誤: {e}"}), 500"""


@edit_bp.route("/edit")
def edit():
    """
    處理編輯角色的頁面請求。
    """
    file_id = request.args.get("file_id")
    if not file_id:
        # 使用 logger 記錄錯誤，並返回清晰的錯誤訊息
        logger.warning("缺少角色檔案 ID。")
        return "缺少角色檔案 ID。", 400

    try:
        character_file_entry_obj = get_character_file_entry(file_id)

        if not character_file_entry_obj:
            logger.info(f"共享資料庫中未找到 '{file_id}'，嘗試從檔案讀取。")
            scan_path = current_app.config["SCAN_PATH"]
            reload_result = reload_character_data(scan_path, file_id)

            if isinstance(reload_result, tuple) and len(reload_result ) == 2:
                # 錯誤 jsonify 響應
                return reload_result 
        
            return render_template(
                "edit.html",
                file_id=file_id,
                data=json.dumps(reload_result),
            )
        else:    
            result_content = character_file_entry_obj.get_character_data()
            append_general_data(result_content)

            return render_template(
                "edit.html",
                file_id=file_id,
                data=json.dumps(result_content),
            )
            
    except Exception as e:
        logger.exception(f"處理編輯頁面時發生內部錯誤，檔案ID: {file_id}")
        return f"內部錯誤: {e}", 500
