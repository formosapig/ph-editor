# ph-editor/api/ui_config.py

import importlib
import locale

from flask import Blueprint, jsonify

from config.dropdown_config import dropdown_config_map
from core.shared_data import get_global_general_data, profile_map, scenario_map, get_default_backstage

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
    """提供給下拉選單使用的簡易列表"""
    options = []

    # 提前取出 id=0 的 profile（若存在）
    zero_profile = profile_map.get(0)

    # 除去 0 的 profile
    other_profiles = {k: v for k, v in profile_map.items() if k != 0}

    locale.setlocale(locale.LC_COLLATE, "zh_TW.UTF-8")
    # 將其轉為 options 並根據 name 中文排序
    sorted_profiles = sorted(
        other_profiles.values(), key=lambda p: locale.strxfrm(p.get("name", ""))
    )

    # 初始選項
    options.append({"label": "請選擇", "value": ""})

    # 第二順位是 id = 0 的 profile（若有）
    if zero_profile:
        options.append(
            {
                "label": zero_profile.get("name", f"id:{zero_profile.get('!id', '')}"),
                "value": zero_profile.get("!id", ""),
            }
        )

    # 加入剩下排序後的 options
    for profile in sorted_profiles:
        options.append(
            {
                "label": profile.get("name", f"id:{profile.get('!id', '')}"),
                "value": profile.get("!id", ""),
            }
        )

    dropdown_config = [{
        "displayLabel": "角色選擇",
        "dataKey": "!id",
        "labelKey": "name",
        "options": options,
        "defaultValue": ""
    }]

    return jsonify({"dropdowns": dropdown_config})


@api_ui_config_bp.route("/scenarios", methods=["GET"])
def get_scenario_list():
    """提供給下拉選單使用的簡易列表"""
    options = []

    # 提前取出 id=0 的 scenario（若存在）
    zero_scenario = scenario_map.get(0)

    # 除去 0 的 scenario
    other_scenarios = {k: v for k, v in scenario_map.items() if k != 0}

    locale.setlocale(locale.LC_COLLATE, "zh_TW.UTF-8")
    # 將其轉為 options 並根據 name 中文排序
    sorted_scenarios = sorted(
        other_scenarios.values(), key=lambda p: locale.strxfrm(p.get("title", ""))
    )

    # 初始選項
    options.append({"label": "請選擇", "value": ""})

    # 第二順位是 id = 0 的 scenario（若有）
    if zero_scenario:
        options.append(
            {
                "label": zero_scenario.get("title", f"id:{zero_scenario.get('!id', '')}"),
                "value": zero_scenario.get("!id", ""),
            }
        )

    # 加入剩下排序後的 options
    for scenario in sorted_scenarios:
        options.append(
            {
                "label": scenario.get("title", f"id:{scenario.get('!id', '')}"),
                "value": scenario.get("!id", ""),
            }
        )

    dropdown_config = [{
        "displayLabel": "場景選擇",
        "dataKey": "!id",
        "labelKey": "title",
        "options": options,
        "defaultValue": ""
    }]

    return jsonify({"dropdowns": dropdown_config})


@api_ui_config_bp.route("/backstage_options", methods=["GET"])
def get_backstage_options():
    """提供 backstage 編輯所需的多組下拉選單"""
    dropdowns = []
    general_data = get_global_general_data()

    # ===== 第一組 dropdown：Tag 下拉選單 =====
    tag_list = general_data.get("tag_list", [])
    tag_type_map = general_data.get("tag_styles", {})

    tag_options = []
    for tag in tag_list:
        tag_type = tag.get("type", "")
        tag_type_name = (
            tag_type_map.get(tag_type, {}).get("name", {}).get("zh", tag_type)
        )
        tag_name = tag.get("name", {}).get("zh", f"id:{tag.get('id')}")
        label = f"{tag_type_name}-{tag_name}"

        tag_options.append({"label": label, "value": tag.get("id")})

    dropdowns.append(
        {
            "displayLabel": "標籤",  # or anything fitting your UI
            "dataKey": "!tag_id",
            "labelKey": "tag",
            "options": tag_options,
            "defaultValue": "",
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
            "label": trait.get("trait", {}).get("zh", ""),
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
            "displayLabel": "內在特質(陰影)",
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
