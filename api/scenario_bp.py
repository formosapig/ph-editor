# ph-editor/api/scenario_bp.py
import json
import logging

from flask import Blueprint, Response, jsonify, request
from core.constants import SpecialScenario
from core.shared_data import get_character_file_entry, get_scenario_map, listen_reverberation
from utils.exceptions import NoUpdateRequired


logger = logging.getLogger(__name__)


api_scenario_bp = Blueprint("api_scenario", __name__, url_prefix="/api/scenario")


@api_scenario_bp.route("/detail/<int:scenario_id>", methods=["GET"])
def get_scenario_detail(scenario_id):
    """提供完整 scenario 詳細內容"""
    logger.debug(f"要求 {scenario_id} 的內容。")
    scenario_map = get_scenario_map()
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


@api_scenario_bp.get("/reverberation/<int:year>")
def get_reverberation(year):
    """提供完整 scenario 詳細內容"""
    sn = request.args.get('sn')

    entry = get_character_file_entry(sn)
    if not entry or entry.scenario_id != SpecialScenario.REVERBERATION:
        raise NoUpdateRequired()
    
    echo = listen_reverberation(year)

    return jsonify(echo)