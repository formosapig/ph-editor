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
        item_copy.pop("!status", None)
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
            '''
            # 從資料中取得 resonance ID (這就是你的 !res_id)
            # 如果沒設，預設可以用 3 (半步青春) 作為保底
            res_id = backstage.get("!resonance_id") 

            if profileData and res_id:
                # 1. 取得人生階段資料與最小年齡
                stage = get_lifestage_by_id(int(res_id))
                resonance_age = get_resonance_age(int(res_id))
                
                if stage and resonance_age is not None:
                    # A. 計算年份：出生年份 + 人生階段最小年齡
                    born_value = profileData.get("born")
                    try:
                        # 如果 born 沒填，預設從 2000 年開始
                        base_year = int(born_value) if born_value is not None else 2000
                        final_year = base_year + resonance_age
                    except (ValueError, TypeError):
                        final_year = 2000 + resonance_age

                    # B. 建立虛擬 Scenario
                    new_scenario_id = OFFSET_REVERBERATION + int(profile_id) * 1000 + int(final_year)
                    
                    # C. 組合文字邏輯
                    # scene = stage['short'] (例如：懷春) + profile['name'] (例如：小美)
                    scene_name = f"{stage['short']}{profileData.get('name', '無名氏')}"
                    # plot = stage['desc'] (例如：少女幻想戀愛的可能)
                    plot_text = stage['desc']

                    scenarios[new_scenario_id] = {
                        "!id": new_scenario_id,
                        "scene": scene_name,
                        "year": final_year,
                        "plot": plot_text
                    }

                    # D. 更新回傳狀態
                    item_copy["!scenario_id"] = new_scenario_id
                    backstage['scenario_color'] = "#4A7C59"
                    backstage['age'] = resonance_age
                    
                    #logger.info(f"歲月迴響成功：{scene_name} ({final_year}年)")
                else:
                    logger.warning(f"跳過時空迴響：無效的 Resonance ID {res_id}")
            else:
                # 如果 res_id 是空的，表示「世界靜默」
                logger.info(f"時空迴響靜默：Profile ID {profile_id} 未設定人生共鳴")
            '''    
        elif scenario_id == SpecialScenario.SILHOUETTE:
            # 處理「時光剪影」特殊邏輯
            tag_id = backstage.get("!tag_id")
            tag = backstage.get("tag")
            target_tag = next((item for item in tag_list if item.get("id") == tag_id), {})
            desc = target_tag.get("desc", {}).get("zh", "")
            #logger.debug(f"tag_id: {tag_id}, tag: {tag}, desc: {desc}")
            if tag_id and tag:
                new_scenario_id = OFFSET_SILHOUETTE + tag_id

                scenarios[new_scenario_id] = {
                    "!id": new_scenario_id,
                    "scene": f"{SpecialScenario.SILHOUETTE.label}【{tag}】",
                    "year": 9900 + tag_id,
                    "plot": desc
                }

                item_copy["!scenario_id"] = new_scenario_id
                backstage['scenario_color'] = "#7F8C31"
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

                # 檢查 echo
                if scenarioData.get('!echo') == 1:
                    backstage['scenario_color'] = "#4A7C59"

        clean_metadatas[k] = item_copy

    return clean_metadatas


