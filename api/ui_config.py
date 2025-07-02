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
    options = [{"label": "請選擇", "value": ""}]
    options += [
        {
            "label": profile.get("name", f"id:{profile.get('!id', '')}"),
            "value": profile.get('!id', '')
        }
        for profile in profile_map.values()
    ]
    return jsonify({"options": options})    