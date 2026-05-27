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
from core.constants import SpecialScenario
from core.shared_data import (
    get_general_data,
    get_profile_map,
    get_scenario_map,
    get_metadata_map,
)
from game_data.life_stage_data import get_lifestage_by_id, get_resonance_age

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
    
    
    allowed_fields = {"!id", "name", "!group_id", "born", "height", "cup"}
    profiles = get_profile_map()
    prepared_profiles = {}
    for k, v in profiles.items():
        if k != 0 and v.get("!id") != 0:
            # 只提取白名單中的欄位，建立一個新的小字典
            prepared_profiles[k] = {key: v[key] for key in v if key in allowed_fields}

    prepared_scenarios = _prepare_scenarios(get_scenario_map())

    prepared_metadatas = _prepare_metadatas(general_data, prepared_profiles, prepared_scenarios, get_metadata_map())

    return {
        "profiles": prepared_profiles,
        "scenarios": prepared_scenarios,
        "metadatas": prepared_metadatas,
        "tag_styles": general_data.get('tag_styles', ""),
        "tag_list": general_data.get('tag_list', ""),
        "profile_group": general_data.get('profile_group', "")
    }

def _prepare_scenarios(scenarios):
    prepared_scenarios = {}

    for k, v in scenarios.items():
        try:
            if int(k) > 0 and v.get("!id"):
                item = copy.deepcopy(v)
                item.pop("notes", None)
                prepared_scenarios[k] = item
        except (ValueError, TypeError):
            continue

    return prepared_scenarios    


# 定義區間常數，方便日後管理
OFFSET_REVERBERATION = 2000000
OFFSET_SILHOUETTE    = 9000000
def _prepare_metadatas(general_data, profiles, scenarios, metadatas):
    tag_styles = general_data.get('tag_styles', {})
    tag_list = general_data.get('tag_list', [])

    type_to_color = {
        t_type: info.get('color', '#555')
        for t_type, info in tag_styles.items()
    }
    
    tag_id_to_color = {
        tag['id']: type_to_color.get(tag.get('type'), '#555')
        for tag in tag_list if 'id' in tag
    }
        

    # 1. 先建立 type 到完整樣式的索引
    type_to_styles = {
        t_type: {
            'color': info.get('color', '#555'),
            'background': info.get('background', '#eee') # 假設預設背景是淡灰色
        }
        for t_type, info in tag_styles.items()
    }

    # 2. 再建立 tag_id 到樣式物件的索引
    tag_id_to_styles = {
        tag['id']: type_to_styles.get(tag.get('type'), {'color': '#555', 'background': '#eee'})
        for tag in tag_list if 'id' in tag
    }

    clean_metadatas = {}

    for k, v in metadatas.items():
        item_copy = copy.deepcopy(v)
        item_copy.pop("!remark", None)
        backstage = item_copy.setdefault('backstage', {})
        backstage.pop("notes", None)
        tag_id = backstage.get('!tag_id')
        
        backstage['color'] = tag_id_to_styles.get(tag_id, {}).get('color', None)
        backstage['background'] = tag_id_to_styles.get(tag_id, {}).get('background', None)
        
        scenario_id = item_copy.get("!scenario_id")
        profile_id = item_copy.get("!profile_id")
       
        # 處理「歲月迴響」特殊邏輯
        if scenario_id == SpecialScenario.REVERBERATION and profile_id:
            profileData = profiles.get(profile_id)
        elif scenario_id == SpecialScenario.SILHOUETTE:
            tag_id = backstage.get("!tag_id")
            target_tag = next((item for item in tag_list if item.get("id") == tag_id), {})
            
            raw_sub_of = target_tag.get("sub_of")
            base_tag_id = int(raw_sub_of) if raw_sub_of else tag_id
            base_tag = next((item for item in tag_list if item.get("id") == base_tag_id), target_tag)
            
            new_scenario_id = OFFSET_SILHOUETTE + base_tag_id
            
            # 初始化場景 (如果已存在則不重複覆蓋)
            if new_scenario_id not in scenarios:
                scenarios[new_scenario_id] = {
                    "!id": new_scenario_id,
                    "scene": f"{SpecialScenario.SILHOUETTE.label}【{base_tag.get('name', {}).get('zh', '')}】",
                    "year": 9900 + base_tag_id,
                    "plot": base_tag.get("desc", {}).get("zh", "") # 父描述
                }
            
            # 如果這是子標籤，將其描述存入 sub_plot
            if raw_sub_of:
                scenarios[new_scenario_id]["sub_plot"] = target_tag.get("desc", {}).get("zh", "")

            item_copy["!scenario_id"] = new_scenario_id
            backstage['scenario_color'] = "#7F8C31"
        else:
            # 計算 age...
            scenarioData = scenarios.get(scenario_id, None)
            profileData = profiles.get(profile_id, None)
            if scenarioData and profileData:
                year = scenarioData.get('year', None)
                born = profileData.get('born', None)
                if year and born:
                    backstage['age'] = year - born

                # 檢查 echo
                if scenarioData.get('!echo') == 1:
                    backstage['scenario_color'] = "#4A7C59"

        clean_metadatas[k] = item_copy

    # 遍歷 scenarios 進行最後的排版與清理
    for _, data in scenarios.items():
        sub_plot = data.pop("sub_plot", None) # 取出並移除 sub_plot
        if sub_plot:
            data["plot"] = f"{data['plot']}\n+\n{sub_plot}".strip()

    return clean_metadatas


