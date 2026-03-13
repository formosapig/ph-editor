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
    profile_map = get_profile_map()
    general_data = get_general_data()
    group_list = general_data.get("profile_group", [])
    
    # 1. 建立 Group 查找表：id -> {order, name}
    group_info = {
        g["id"]: {
            "order": g.get("order", 999), 
            "name": g.get("name", {}).get("zh", "未命名分組")
        } for g in group_list
    }
    
    # 2. 排除 ID 0 (新角色)
    other_profiles = [p for k, p in profile_map.items() if k != 0]

    # 3. 排序：Group Order -> Born
    def sort_key(p):
        g_id = p.get("!group_id", 0)
        group_order = group_info.get(g_id, {}).get("order", 9999) if g_id != 0 else 9999
        return (group_order, p.get("born", 0))

    sorted_profiles = sorted(other_profiles, key=sort_key)

    # 4. 處理分組標題
    profile_options = []
    current_group_id = None

    for profile in sorted_profiles:
        p_group_id = profile.get("!group_id", 0)
        
        # 檢查是否需要插入分組標題
        if p_group_id != 0 and p_group_id != current_group_id:
            group_name = group_info.get(p_group_id, {}).get("name", "其他")
            profile_options.append({"id": "", "name": f"👥 {group_name}", "disabled": True})
            current_group_id = p_group_id
        elif p_group_id == 0 and current_group_id != 0 and current_group_id is not None:
            profile_options.append({"id": "", "name": "👤 未分組", "disabled": True})
            current_group_id = 0

        profile_options.append({
            "id": profile.get("!id", ""),
            "name": profile.get("name", f"id:{profile.get('!id', '')}"),
            "disabled": False
        })

    # 將資料轉為 JSON 字串傳給 Template
    return render_template("epoch.html", profile_options=profile_options)
    