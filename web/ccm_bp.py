# ph-editor/web/ccm_bp.py
import copy
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
ccm_bp = Blueprint("ccm_bp", __name__, url_prefix="/ccm")
  
@ccm_bp.get("")
def ccm_view():
    data = _get_ccm_data()
    return render_template("ccm.html", **data) # 使用 ** 解封字典傳入模板

@ccm_bp.get("/reload")
def ccm_reload():
    data = _get_ccm_data()
    return jsonify(data), 200

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
        if k > 0 and v.get("!id") != 0
    }

    metadatas = get_metadata_map()

    return {
        "profiles": clean_profiles,
        "scenarios": clean_scenarios,
        "metadatas": _get_clean_metadatas(general_data, get_metadata_map()), #metadatas,
        "tag_styles": general_data.get('tag_styles', ""),
        "tag_list": general_data.get('tag_list', ""),
        "profile_group": general_data.get('profile_group', "")
    }

def _get_clean_metadatas(general_data, metadatas):
    tag_styles = general_data.get('tag_styles', {})
    tag_list = general_data.get('tag_list', [])

    # 1. 直接建立 tag_id -> color 的快速對照表
    # 先建立 type -> color 的對照，避免在迴圈內反覆 .get()
    type_to_color = {
        t_type: info.get('color', '#555') 
        for t_type, info in tag_styles.items()
    }
    
    # 建立最終的 tag_id -> color 對照表
    tag_id_to_color = {
        tag['id']: type_to_color.get(tag.get('type'), '#555')
        for tag in tag_list if 'id' in tag
    }
        
    clean_metadatas = {}

    for k, v in metadatas.items():
        item_copy = copy.deepcopy(v)
        backstage = item_copy.setdefault('backstage', {})
        tag_id = backstage.get('!tag_id')
        backstage['border_color'] = tag_id_to_color.get(tag_id, '#555')
        clean_metadatas[k] = item_copy

    return clean_metadatas


