# ph-editor/web/edit_bp.py
import json
import logging
from flask import (
    Blueprint,
    current_app,
    render_template,
    request,
)

# get_character_data 會處理延遲解析邏輯
from core.shared_data import (
    add_or_update_character_with_path,
    find_another_sn_by_scenario_id,
    get_character_file_entry,
)
from utils.character_file_utils import (
    #reload_character_data,
    append_general_data,
)

edit_bp = Blueprint("edit_bp", __name__)


logger = logging.getLogger(__name__)
#logger.disabled = True


@edit_bp.route("/edit/<sn>")
def edit(sn):
    """
    處理編輯角色的頁面請求。
    """
    try:
        entry = get_character_file_entry(sn)
        if not entry:
            raise FileNotFoundError(f"找不到 SN: '{sn}' 的資料。")
        result_content = entry.get_character_data()
        append_general_data(result_content)

        sub_sn = find_another_sn_by_scenario_id(entry.scenario_id, sn)
        
        return render_template(
            "edit.html",
            sn = sn,
            sub_sn = sub_sn,  # sub file 我們並不編輯它，只秀截圖
            file_id = entry.file_id,
            remark = entry.get_remark(),
            status = entry.get_status(),
            data = json.dumps(result_content),
        )
    
    except FileNotFoundError as fnfe:
        # 處理找不到檔案的特定例外
        logger.exception(f"找不到角色檔案 '{sn}'。")
        return f"找不到指定的角色檔案: {sn}", 404
        
    except Exception as e:
        logger.exception(f"處理編輯頁面時發生內部錯誤，檔案ID: {sn}")
        return f"內部錯誤: {e}", 500
