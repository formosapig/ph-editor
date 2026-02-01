# ph-editor/web/general_bp.py
import logging
import json
import traceback
from flask import (
    Blueprint,
    current_app,
    jsonify,
    render_template,
    request,
)
from core.shared_data import (
    get_general_data,
    update_general_data,
)


logger = logging.getLogger(__name__)


general_bp = Blueprint("general_bp", __name__)


@general_bp.route("/general")
def general():
    general_data = get_general_data()
    color_traits_data = general_data["color_traits"]
    tag_styles_data = general_data["tag_styles"]
    tag_list_data = general_data["tag_list"]
    profile_group_data = general_data["profile_group"]

    return render_template(
        "general.html",
        color_traits = color_traits_data,
        tag_styles = tag_styles_data,
        tag_list = tag_list_data,
        profile_group = profile_group_data,
    )


@general_bp.route("/general/update", methods=["POST"])
def update_general_settings():
    """
    接收前端傳送的全域設定資料（特質-顏色、標籤類型、標籤），並更新到儲存中。
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "請求中沒有 JSON 資料"}), 400

        # 從接收到的資料中提取各個設定部分
        color_traits = data.get("color_traits")
        tag_styles = data.get("tag_styles")
        tag_list = data.get("tag_list")
        profile_group = data.get("profile_group")
        
        #logger.debug("更新全域資料：")
        #logger.debug(json.dumps(data, ensure_ascii=False, indent=2))

        # 進行資料驗證 (這裡可以根據你的需求添加更嚴格的驗證邏輯)
        if color_traits is None or tag_styles is None or tag_list is None:
            return (
                jsonify(
                    {
                        "message": (
                            "缺少必要的設定資料 "
                            "(color_traits, tag_styles, tag_list)"
                        )
                    }
                ),
                400,
            )

        # 取得目前的 general_data
        #current_general_data = get_general_data()

        # 更新 general_data 的相關欄位
        #current_general_data["color_traits"] = color_traits
        #current_general_data["tag_styles"] = tag_styles
        #current_general_data["tag_list"] = tag_list

        # 呼叫 function 來更新全域設定資料
        # 假設 update_global_general_data 負責將資料寫入檔案或資料庫
        # 視為新增版本
        #update_general_data(current_general_data)
        update_general_data(data)

        return jsonify({"message": "全域設定更新成功！"}), 200

    except Exception as e:
        current_app.logger.error(f"更新全域設定時發生錯誤: {traceback.format_exc()}")
        return (
            jsonify(
                {
                    "message": f"伺服器內部錯誤: {str(e)}",
                    "detail": traceback.format_exc(),
                }
            ),
            500,
        )
