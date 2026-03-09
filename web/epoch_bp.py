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
from utils.exceptions import APIError, ErrorTest

logger = logging.getLogger(__name__)
epoch_bp = Blueprint("epoch_bp", __name__, url_prefix="/epoch")
  
@epoch_bp.get("")
def epoch_view():
    data = {} # _get_ccm_data()
    raise ErrorTest() #APIError("這是錯誤測試", 500)        
    return render_template("epoch.html", **data) # 使用 ** 解封字典傳入模板
    