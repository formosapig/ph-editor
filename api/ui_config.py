# ph-editor/api/ui_config.py
import importlib
import locale
import logging

from flask import Blueprint, jsonify

from config.dropdown_config import dropdown_config_map
from core.constants import SpecialScenario
from core.shared_data import (
    get_general_data,
    get_profile_map,
    get_scenario_map,
    get_default_backstage,
    get_tag_count,
    get_color_trait_count,
)
from game_data.cup_data import generate_cup_options

logger = logging.getLogger(__name__)

api_ui_config_bp = Blueprint("api_ui_config", __name__, url_prefix="/api/ui_config")


@api_ui_config_bp.route("/options/<tab>/<subTab>", methods=["GET"])
def get_dropdown_options(tab, subTab):
    config_key = (tab, subTab)
    dropdowns = []

    if config_key not in dropdown_config_map:
        return jsonify({"dropdowns": []})

    for item in dropdown_config_map[config_key]:
        try:
            # 匯入模組
            data_module = importlib.import_module(f"game_data.{item['module']}")
            base_data = getattr(data_module, item["attribute"])

            # 如果有 subKey，則取內部子資料
            data_list = base_data
            if "subKey" in item:
                data_list = base_data.get(item["subKey"], [])

            # 語系處理
            lang = item.get("lang", "zh")

            # 建立下拉選單項目
            options = [
                {
                    "label": entry["name"].get(lang, f"id:{entry['id']}"),
                    "value": entry["id"],
                }
                for entry in data_list
            ]

            dropdowns.append(
                {
                    "displayLabel": item["displayLabel"],
                    "dataKey": item["dataKey"],
                    "labelKey": item["labelKey"],
                    "options": options,
                    "defaultValue": "",
                }
            )

        except Exception as e:
            print(f"[錯誤] 載入資料失敗: {e}")

    return jsonify({"dropdowns": dropdowns})


@api_ui_config_bp.route("/profiles", methods=["GET"])
def get_profile_list():
    profile_map = get_profile_map()
    general_data = get_general_data()
    group_list = general_data.get("profile_group", [])
    
    # 建立 Group 查找表：id -> {order, name}
    group_info = {g["id"]: {"order": g.get("order", 999), "name": g.get("name", {}).get("zh", "未命名分組")} 
                  for g in group_list}
    
    # --- 第一部分：Profile 下拉選單資料處理 ---
    zero_profile = profile_map.get(0)
    other_profiles = [p for k, p in profile_map.items() if k != 0]

    # 排序邏輯：1. Group Order, 2. Born
    def sort_key(p):
        g_id = p.get("!group_id", 0)
        group_order = group_info.get(g_id, {}).get("order", 9999) if g_id != 0 else 9999
        born_val = p.get("born", 0)
        return (group_order, born_val)

    sorted_profiles = sorted(other_profiles, key=sort_key)

    profile_options = [{"label": "請選擇角色", "value": ""}]
    if zero_profile:
        profile_options.append({
            "label": zero_profile.get("name", f"id:{zero_profile.get('!id', '')}"),
            "value": zero_profile.get("!id", ""),
        })

    current_group_id = None
    for profile in sorted_profiles:
        p_group_id = profile.get("!group_id", 0)
        # 插入分組標題
        if p_group_id != 0 and p_group_id != current_group_id:
            group_name = group_info.get(p_group_id, {}).get("name", "其他")
            profile_options.append({"label": f"👥{group_name}", "value": "", "disabled": True})
            current_group_id = p_group_id
        elif p_group_id == 0 and current_group_id != 0 and current_group_id is not None:
            profile_options.append({"label": "👤未分組", "value": "", "disabled": True})
            current_group_id = 0

        profile_options.append({
            "label": profile.get("name", f"id:{profile.get('!id', '')}"),
            "value": profile.get("!id", ""),
        })

    # --- 第二部分：Profile Group 下拉選單資料處理 ---
    # 按 order 排序 group 列表
    sorted_group_list = sorted(group_list, key=lambda g: g.get("order", 999))
    
    group_options = [
        {"label": "無", "value": 0}
    ]
    for g in sorted_group_list:
        group_options.append({
            "label": g.get("name", {}).get("zh", f"Group:{g.get('id')}"),
            "value": g.get("id")
        })

    # --- 第三部分：罩杯尺寸選單 ---
    # 直接從 cup_data 模組獲取處理好的選項
    cup_options = generate_cup_options()

    # --- 整合輸出 ---
    dropdown_configs = [
        {
            "displayLabel": "角色選擇",
            "dataKey": "!id",
            "labelKey": "name",
            "options": profile_options,
            "defaultValue": ""
        },
        {
            "displayLabel": "角色分組",
            "dataKey": "!group_id",
            "labelKey": "group",
            "options": group_options,
            "defaultValue": 0
        },
        {
            "displayLabel": "罩杯",
            "dataKey": "cup",
            "labelKey": "cup",
            "options": cup_options,
            "defaultValue": "34D"
        }
    ]

    return jsonify({"dropdowns": dropdown_configs})
    
    
@api_ui_config_bp.get("/scenarios")
def get_scenario_list():
    scenario_map = get_scenario_map()
    
    special_features = [
        SpecialScenario.NEW,
        SpecialScenario.SILHOUETTE,
        SpecialScenario.REVERBERATION
    ]

    special_ids = {int(s) for s in SpecialScenario}
    other_scenarios = {k: v for k, v in scenario_map.items() if k not in special_ids}

    locale.setlocale(locale.LC_COLLATE, "zh_TW.UTF-8")
    # 將其轉為 options 並根據 name 中文排序
    sorted_scenarios = sorted(
        other_scenarios.values(),
        key=sort_key_with_int_year
    )

    options = []
    
    # 初始選項
    options.append({"label": "請選擇", "value": "", "disabled": True})

    # 特殊場景
    for spec in special_features:
        spec_data = scenario_map.get(int(spec), {})
        label = spec_data.get("scene", spec.label)
        options.append({
            "label": label,
            "value": int(spec)
        })

    # 加入剩下排序後的 options
    for scenario in sorted_scenarios:
        # 嘗試從 scenario 取得 "scene" 和 "year"
        scene = scenario.get("scene", f"id:{scenario.get('!id', '')}")
        year = scenario.get("year")
        scenario_id = scenario.get("!id", "")

        # 根據是否有 "year" 來建構 label 格式
        if year:
            label = f"{scene}({year})"
        else:
            label = scene  # 如果沒有 year，則保持原來的 scene(標題)

        options.append({
            "label": label,
            "value": scenario_id,
        })

    season_options = [
        {"label": "無", "value": ""},
        {"label": "🌸春", "value": "spring"},
        {"label": "☀️夏", "value": "summer"},
        {"label": "🍁秋", "value": "autumn"},
        {"label": "❄️冬", "value": "winter"}
    ]

    dropdown_config = [
        {
            "displayLabel": "場景選擇",
            "dataKey": "!id",
            "labelKey": "scene",
            "options": options,
            "defaultValue": ""
        },
        {
            "displayLabel": "季節",
            "dataKey": "season",
            "labelKey": "",
            "options": season_options,
            "defaultValue": ""
        }
    ]

    return jsonify({"dropdowns": dropdown_config})


def sort_key_with_int_year(scenario):
    """ 供 get_scenario_list 使用 """
    year_value = scenario.get("year")
    scene = scenario.get("scene", "")
    
    # 檢查 year_value 是否為 None (缺失值)
    if year_value is None:
        # 1. Flag: 1 (排在後面)
        # 2. Year_Value: 使用一個極大的值，確保排在所有有效年份之後
        # 3. Scene: 用於缺失年份之間的排序
        return (1, float('inf'), locale.strxfrm(scene))
    else:
        # 1. Flag: 0 (排在前面)
        # 2. Year_Value: 實際的年份數字 (假設是 int 或 float)
        # 3. Scene: 用於年份相同時的次要排序
        return (0, year_value, locale.strxfrm(scene))
                

@api_ui_config_bp.route("/backstage_options", methods=["GET"])
def get_backstage_options():
    """提供 backstage 編輯所需的多組下拉選單"""
    dropdowns = []
    general_data = get_general_data()

    # ===== 第一組 dropdown：Tag 下拉選單 =====
    tag_list = general_data.get("tag_list", [])
    tag_type_map = general_data.get("tag_styles", {})

    default_tag_id = tag_list[0].get("id") if tag_list and tag_list[0].get("id") is not None else ""

    tag_options = []
    processed_tag_types = set() # 用來追蹤已經處理過的 tag_type，避免重複添加標題

    for tag in tag_list:
        tag_type = tag.get("type", "")
        tag_type_name = (
            tag_type_map.get(tag_type, {}).get("name", {}).get("zh", tag_type)
        )
        tag_name = tag.get("name", {}).get("zh", f"id:{tag.get('id')}")

        # 1. 檢查是否已經添加過該 tag_type 的標題
        if tag_type not in processed_tag_types:
            # 添加 tag_type_name 作為一個不可選的選項 (標題)
            tag_options.append({
                "label": f"🗂️{tag_type_name}",
                "value": "",
                "disabled": True
            })
            processed_tag_types.add(tag_type)

        # 2. 添加 tag_name 作為可選選項
        tag_options.append({
            "label": (
                f"{tag_name} ({c})" if (c := get_tag_count(tag.get("id"))) > 0
                else tag_name
            ),
            "pureLabel": tag_name,
            "value": tag.get("id")
        })

    dropdowns.append(
        {
            "displayLabel": "標籤",  # or anything fitting your UI
            "dataKey": "!tag_id",
            "labelKey": "tag",
            "options": tag_options,
            "defaultValue": default_tag_id,
        }
    )

    # ===== 第二 & 第三組 dropdown：Color Trait 下拉選單 =====
    color_traits = general_data.get("color_traits", [])

    #color_options = [
    #    {
    #        "label": trait.get("trait", {}).get("zh", ""),
    #        "value": trait.get("code"),  # or index
    #    }
    #    for trait in color_traits
    #]
    color_options = [
        {"label": "無", "value": ""},  # 或 value: "none"
    ] + [
        {
            "label": (
                f"{trait.get('trait', {}).get('zh', '')} ({c})" if (c := get_color_trait_count(trait.get("code"))) > 0 
                else trait.get('trait', {}).get('zh', '')
            ),
            "pureLabel": trait.get("trait", {}).get("zh", ""),
            "value": trait.get("code"),
        }
        for trait in color_traits
    ]

    dropdowns.append(
        {
            "displayLabel": "外顯特質(面具)",
            "dataKey": "!persona_code",
            "labelKey": "persona",
            "options": color_options,
            "defaultValue": "",
        }
    )

    dropdowns.append(
        {
            "displayLabel": "內隱特質(陰影)",
            "dataKey": "!shadow_code",
            "labelKey": "shadow",
            "options": color_options,
            "defaultValue": "",
        }
    )

    # 取得預設情境模板
    default_backstage_data = get_default_backstage()

    return jsonify({
        "dropdowns": dropdowns ,
        "defaultBackstage" : default_backstage_data
    })
