# ph-editor/web/edit_bp.py
import json
import logging
from flask import (
    Blueprint,
    render_template,
)

# get_character_data 會處理延遲解析邏輯
from core.shared_data import (
    find_another_sn_by_scenario_id,
)
from utils.character_file_utils import (
    #reload_character_data,
    append_general_data,
)
from utils.decorators import inject_character_file_entry

edit_bp = Blueprint("edit_bp", __name__)


logger = logging.getLogger(__name__)
#logger.disabled = True


@edit_bp.route("/edit/<sn>")
@inject_character_file_entry
def edit(sn, entry):
    """
    處理編輯角色的頁面請求。
    """
    result_content = entry.get_character_data()
    append_general_data(result_content)

    sub_sn = find_another_sn_by_scenario_id(entry.scenario_id, sn)
    
    return render_template(
        "edit.html",
        sn=sn,
        sub_sn=sub_sn,  # sub file 我們並不編輯它，只秀截圖
        file_id=entry.file_id,
        remark=entry.get_remark(),
        status=entry.get_status(),
        data=json.dumps(result_content), # 注意, 如果丟 dict 去前端, json 的 key 會跑掉
    )    