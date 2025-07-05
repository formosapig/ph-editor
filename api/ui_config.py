# ph-editor/api/ui_config.py

import importlib
from flask import Blueprint, jsonify
from config.dropdown_config import dropdown_config_map
from core.shared_data import profile_map

api_ui_config_bp = Blueprint('api_ui_config', __name__, url_prefix='/api/ui_config')

@api_ui_config_bp.route('/options/<tab>/<subTab>', methods=['GET'])
def get_dropdown_options(tab, subTab):
    config_key = (tab, subTab)
    dropdowns = []

    if config_key not in dropdown_config_map:
        return jsonify({"dropdowns": []})

    for item in dropdown_config_map[config_key]:
        try:
            # 匯入模組
            data_module = importlib.import_module(f"game_data.{item['module']}")
            base_data = getattr(data_module, item['attribute'])

            # 如果有 subKey，則取內部子資料
            data_list = base_data
            if 'subKey' in item:
                data_list = base_data.get(item['subKey'], [])

            # 語系處理
            lang = item.get('lang', 'zh')

            # 建立下拉選單項目
            options = [
                {
                    "label": entry['name'].get(lang, f"id:{entry['id']}"),
                    "value": entry['id']
                }
                for entry in data_list
            ]

            dropdowns.append({
                "displayLabel": item["displayLabel"],
                "dataKey": item["dataKey"],
                "labelKey": item["labelKey"],
                "options": options,
                "defaultValue": ""
            })

        except Exception as e:
            print(f"[錯誤] 載入資料失敗: {e}")

    return jsonify({"dropdowns": dropdowns})
    
@api_ui_config_bp.route('/profiles', methods=['GET'])
def get_profile_list():
    """提供給下拉選單使用的簡易列表"""
    options = []

    # 提前取出 id=0 的 profile（若存在）
    zero_profile = profile_map.get(0)

    # 除去 0 的 profile
    other_profiles = {
        k: v for k, v in profile_map.items() if k != 0
    }

    # 將其轉為 options 並根據 name 中文排序
    sorted_profiles = sorted(
        other_profiles.values(),
        key=lambda p: p.get("name", "")
    )

    # 初始選項
    options.append({"label": "請選擇", "value": ""})

    # 第二順位是 id = 0 的 profile（若有）
    if zero_profile:
        options.append({
            "label": zero_profile.get("name", f"id:{zero_profile.get('!id', '')}"),
            "value": zero_profile.get("!id", "")
        })

    # 加入剩下排序後的 options
    for profile in sorted_profiles:
        options.append({
            "label": profile.get("name", f"id:{profile.get('!id', '')}"),
            "value": profile.get("!id", "")
        })

    return jsonify({"options": options})