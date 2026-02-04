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
    
        general_data = get_general_data()
        profile_group = general_data.get('profile_group', "")
        tag_styles = general_data.get('tag_styles', "")
        tag_list = general_data.get('tag_list', "")
    
        profiles = get_profile_map()
        # 過濾：Key 不為 0 且 內部的 !id 也不為 0
        clean_profiles = {
            k: v for k, v in profiles.items()
            if k != 0 and v.get("!id") != 0
        }
    
        scenarios = get_scenario_map()
        # 同樣邏輯過濾場景
        clean_scenarios = {
            k: v for k, v in scenarios.items()
            if k != 0 and v.get("!id") != 0
        }
    
        metadatas = get_metadata_map()

        # 2. 將資料渲染進模板
        return render_template(
            "ccm.html",
            profiles = clean_profiles,
            scenarios = clean_scenarios,
            metadatas = metadatas,
            tag_styles = tag_styles,
            tag_list = tag_list,
            profile_group = profile_group
        )

    except Exception as e:
        logger.error(f"渲染 CCM 頁面失敗: {traceback.format_exc()}")
        # 如果出錯，可以導向錯誤頁面或回傳錯誤訊息
        return render_template("error.html", message="無法讀取 CCM 資料"), 500
        
@ccm_bp.route("/api/ccm/data")
def get_ccm_data():
    """ 獲取 CCM 矩陣所需的完整資料包 """
    try:
        #data = {
        #    "profiles": get_all_profiles(),     # Template: Profile
        #    "scenarios": get_all_scenarios(),   # Template: Scenario
        #    "backstages": get_all_backstages(), # Template: Backstage
        #}
        #return jsonify(data), 200
        # 這裡就是你切好的三個 Template 實體化後的資料
        data = {
            "profiles": [
                {"id": 1, "name": "許母IF", "persona": "三兇-臉兇"},
                {"id": 2, "name": "許秀芬IF", "persona": "三兇-乳兇"},
                {"id": 3, "name": "九条幽", "persona": "三兇-脾氣兇"}
            ],
            "scenarios": [
                {"id": 101, "year": 1997, "title": "落榜之夜"},
                {"id": 102, "year": 1998, "title": "雞湯練習"},
                {"id": 103, "year": 1999, "title": "覺醒瞬間"}
            ],
            "backstages": [
                {"scenario_id": 101, "profile_id": 1, "tag": "設定-virgin", "code": "#FFC0CB"},
                {"scenario_id": 101, "profile_id": 2, "tag": "設定-virgin", "code": "#FFC0CB"},
                {"scenario_id": 102, "profile_id": 3, "tag": "暴食期", "code": "#800080"},
                {"scenario_id": 103, "profile_id": 1, "tag": "覺醒", "code": "#FF0000"},
                {"scenario_id": 103, "profile_id": 2, "tag": "犧牲", "code": "#4B0082"}
            ]
        }
        return jsonify(data)
    
    except Exception as e:
        logger.error(f"獲取 CCM 資料失敗: {traceback.format_exc()}")
        return jsonify({"message": "無法讀取資料", "error": str(e)}), 500

@ccm_bp.route("/api/ccm/update_backstage", methods=["POST"])
def update_backstage():
    """ 
    接收場景工作台傳回的批次 Backstage 更新。
    解決「改 A 女漏 B 女」的問題：前端會一次傳回該場景下所有角色的 Backstage。
    """
    try:
        data = request.get_json()
        if not data or "backstages" not in data:
            return jsonify({"message": "無效的資料格式"}), 400

        # 批次寫入資料庫或 JSON 檔案
        #update_backstage_batch(data["backstages"])

        return jsonify({"message": "時空因果同步成功！"}), 200
    except Exception as e:
        current_app.logger.error(f"更新 Backstage 時發生錯誤: {traceback.format_exc()}")
        return jsonify({"message": f"伺服器錯誤: {str(e)}"}), 500