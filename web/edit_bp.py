# ph-editor/web/edit_bp.py
import json
import logging
from flask import (
    Blueprint,
    jsonify,
    render_template,
)

# get_character_data 會處理延遲解析邏輯
from core.shared_data import (
    #find_another_sn_by_scenario_id,
    get_info_by_tag_id,
)
from utils.character_file_utils import (
    #reload_character_data,
    append_general_data,
)
from utils.decorators import inject_character_file_entry

edit_bp = Blueprint("edit_bp", __name__)


logger = logging.getLogger(__name__)
#logger.disabled = True


@edit_bp.get("/edit/<sn>")
@inject_character_file_entry
def edit(sn, entry):
    """
    處理編輯角色的頁面請求。
    """
    result_content = entry.get_character_data()
    append_general_data(result_content)

    #sub_sn = find_another_sn_by_scenario_id(entry.scenario_id, sn)
    correct = entry.get_correct()[1]
    info = get_info_by_tag_id(entry.tag_id)
    profile = entry.get_profile()
    scenario = entry.get_scenario()
    backstage = entry.get_backstage()
    final_data = {
        key: "\n".join(filter(None, [info.get(key), profile.get(key), scenario.get(key), backstage.get(key)]))
        for key in ["soul", "meat", "form", "code"]
    }

    return render_template(
        "edit.html",
        sn=sn,
        #sub_sn=sub_sn,  # sub file 我們並不編輯它，只秀截圖
        file_id=entry.file_id,
        remark=entry.get_remark(),
        correct=correct,
        soul=final_data["soul"],
        meat=final_data["meat"],
        form=final_data["form"],
        code=final_data["code"],
        data=json.dumps(result_content), # 注意, 如果丟 dict 去前端, json 的 key 會跑掉
    )


@edit_bp.patch("/edit/<sn>")
@inject_character_file_entry
def patch_data(sn, entry):
    """
    處理編輯角色的頁面請求。
    """
    # 特別重新讀取二進制資料
    entry.reload_binary()
    #result_content = entry.get_character_data()
    #append_general_data(result_content)

    #sub_sn = find_another_sn_by_scenario_id(entry.scenario_id, sn)
    correct = entry.get_correct()[1]
    info = get_info_by_tag_id(entry.tag_id)
    profile = entry.get_profile()
    scenario = entry.get_scenario()
    backstage = entry.get_backstage()
    final_data = {
        key: "\n".join(filter(None, [info.get(key), profile.get(key), scenario.get(key), backstage.get(key)]))
        for key in ["soul", "meat", "form", "code"]
    }

    return jsonify({
        "file_id": entry.file_id,
        "correct": correct,
        "soul": final_data["soul"],
        "meat": final_data["meat"],
        "form": final_data["form"],
        "code": final_data["code"],
    })
