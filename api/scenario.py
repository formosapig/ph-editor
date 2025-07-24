# ph-editor/api/scenario.py
import json

from flask import Blueprint, Response

from core.shared_data import scenario_map

api_scenario_bp = Blueprint("api_scenario", __name__, url_prefix="/api/scenario")


@api_scenario_bp.route("/detail/<int:scenario_id>", methods=["GET"])
def get_scenario_detail(scenario_id):
    """提供完整 scenario 詳細內容"""
    scenario = scenario_map.get(scenario_id)
    if scenario:
        return Response(
            json.dumps(scenario, ensure_ascii=False, indent=2),
            content_type="application/json",
        )
    else:
        return Response(
            json.dumps(
                {"error": f"找不到 ID 為 {scenario_id} 的場景"},
                ensure_ascii=False,
                indent=2,
            ),
            status=404,
            content_type="application/json",
        )
