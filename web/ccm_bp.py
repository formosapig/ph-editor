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

    prepared_scenarios = _prepare_scenarios(get_scenario_map())

    prepared_metadatas = _prepare_metadatas(general_data, clean_profiles, prepared_scenarios, get_metadata_map())

    return {
        "profiles": clean_profiles,
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
        
    clean_metadatas = {}

    for k, v in metadatas.items():
        item_copy = copy.deepcopy(v)
        backstage = item_copy.setdefault('backstage', {})
        tag_id = backstage.get('!tag_id')
        
        backstage['border_color'] = tag_id_to_color.get(tag_id, '#555')
        
        scenario_id = item_copy.get("!scenario_id")
        profile_id = item_copy.get("!profile_id")

        # 處理「歲月迴響」特殊邏輯
        if scenario_id == SpecialScenario.REVERBERATION and profile_id:
            profileData = profiles.get(profile_id)

            if profileData:
                born_value = profileData.get("born")
                try:
                    final_year = int(born_value) + 20 if born_value is not None else 2000
                except (ValueError, TypeError):
                    final_year = 2000

                # 2. 建立虛擬 Scenario
                new_scenario_id = OFFSET_REVERBERATION + int(profile_id)
                scenarios[new_scenario_id] = {
                    "!id": new_scenario_id,
                    "scene": SpecialScenario.REVERBERATION.label,
                    "year": final_year,
                    "plot": "半步青春"
                }

                item_copy["!scenario_id"] = new_scenario_id
                backstage['border_color'] = "#39FF14"
                backstage['age'] = 20
            else:
                logger.error(f"跳過時空迴響：找不到 Profile ID {profile_id}")
        elif scenario_id == SpecialScenario.SILHOUETTE:
            # 處理「時光剪影」特殊邏輯
            tag_id = backstage.get("!tag_id")
            tag = backstage.get("tag")
            target_tag = next((item for item in tag_list if item.get("id") == tag_id), {})
            desc = target_tag.get("desc", {}).get("zh", "")
            logger.debug(f"tag_id: {tag_id}, tag: {tag}, desc: {desc}")
            if tag_id and tag:
                new_scenario_id = OFFSET_SILHOUETTE + tag_id

                scenarios[new_scenario_id] = {
                    "!id": new_scenario_id,
                    "scene": f"{SpecialScenario.SILHOUETTE.label}【{tag}】",
                    "year": 9900 + tag_id,
                    "plot": desc
                }

                item_copy["!scenario_id"] = new_scenario_id
                #backstage['age'] = '-'
        else:
            # 計算 age...
            scenarioData = scenarios.get(scenario_id, None)
            profileData = profiles.get(profile_id, None)
            if scenarioData and profileData:
                year = scenarioData.get('year', None)
                born = profileData.get('born', None)
                if year and born:
                    backstage['age'] = year - born

        clean_metadatas[k] = item_copy

    return clean_metadatas


