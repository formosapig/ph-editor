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
    find_fild_id_by_scenario_id,
    get_character_file_entry,
)
from utils.character_file_utils import (
    #reload_character_data,
    append_general_data,
)

edit_bp = Blueprint("edit_bp", __name__)


logger = logging.getLogger(__name__)
#logger.disabled = True


@edit_bp.route("/edit")
def edit():
    """
    處理編輯角色的頁面請求。
    """
    file_id = request.args.get("file_id")
    if not file_id:
        # 使用 logger 記錄錯誤，並返回清晰的錯誤訊息
        logger.warning("缺少角色檔案 ID。")
        return "錯誤: 缺少角色檔案 ID。", 400

    try:
        character_file_entry_obj = get_character_file_entry(file_id)

        if not character_file_entry_obj:
            logger.info(f"共享資料庫中未找到 '{file_id}'，嘗試從檔案讀取。")
            scan_path = current_app.config["SCAN_PATH"]
            add_or_update_character_with_path(scan_path, file_id)
            character_file_entry_obj = get_character_file_entry(file_id)
            
        if not character_file_entry_obj:
            raise FileNotFoundError(f"檔案 '{file_id}' 嘗試重新讀取後仍不存在。")
            
        result_content = character_file_entry_obj.get_character_data()
        append_general_data(result_content)

        # 取得使用同一個 scenario id 的 file entry object 
        sub_file_id = find_fild_id_by_scenario_id(character_file_entry_obj.scenario_id, file_id)
        

        return render_template(
            "edit.html",
            file_id = file_id,
            sub_file_id = sub_file_id,
            remark = character_file_entry_obj.get_remark(),
            data = json.dumps(result_content),
        )
    
    except FileNotFoundError as fnfe:
        # 處理找不到檔案的特定例外
        logger.exception(f"找不到角色檔案 '{file_id}'。")
        return f"找不到指定的角色檔案: {file_id}", 404
        
    except Exception as e:
        logger.exception(f"處理編輯頁面時發生內部錯誤，檔案ID: {file_id}")
        return f"內部錯誤: {e}", 500
