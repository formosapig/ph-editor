# ph-editor/web/ccm_bp.py
import logging
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
    get_profile_map,
    get_scenario_map,
    get_metadata_map,
)

logger = logging.getLogger(__name__)
ccm_bp = Blueprint("ccm_bp", __name__)
  
@ccm_bp.route("/ccm")
def ccm_view():
    try:
        data = _get_ccm_data()
        return render_template("ccm.html", **data) # 使用 ** 解封字典傳入模板
    except Exception as e:
        logger.error(f"渲染 CCM 頁面失敗: {traceback.format_exc()}")
        return render_template("error.html", message="無法讀取 CCM 資料"), 500

@ccm_bp.route("/ccm/reload", methods=["GET"])
def ccm_reload():
    """重新讀取資料並以 JSON 格式回傳"""
    try:
        data = _get_ccm_data()
        return jsonify({
            "status": "success",
            "data": data
        }), 200
    except Exception as e:
        logger.error(f"重新載入 CCM 資料失敗: {traceback.format_exc()}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

def _get_ccm_data():
    """封裝資料獲取與過濾的邏輯，供多個 Route 共用"""
    general_data = get_general_data()
    
    profiles = get_profile_map()
    clean_profiles = {
        k: v for k, v in profiles.items()
        if k != 0 and v.get("!id") != 0
    }

    scenarios = get_scenario_map()
    clean_scenarios = {
        k: v for k, v in scenarios.items()
        if k != 0 and v.get("!id") != 0
    }

    metadatas = get_metadata_map()

    return {
        "profiles": clean_profiles,
        "scenarios": clean_scenarios,
        "metadatas": metadatas,
        "tag_styles": general_data.get('tag_styles', ""),
        "tag_list": general_data.get('tag_list', ""),
        "profile_group": general_data.get('profile_group', "")
    }