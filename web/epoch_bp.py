# ph-editor/web/epoch_bp.py
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
epoch_bp = Blueprint("epoch_bp", __name__, url_prefix="/epoch")
  
@epoch_bp.get("")
def epoch_view():
    try:
        data = {} # _get_ccm_data()
        return render_template("epoch.html", **data) # 使用 ** 解封字典傳入模板
    except Exception as e:
        logger.error(f"渲染 CCM 頁面失敗: {traceback.format_exc()}")
        return render_template("error.html", message="無法讀取 CCM 資料"), 500