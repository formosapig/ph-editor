# ph-editor/api/profile.py

import json
from flask import Blueprint, jsonify, Response
from core.shared_data import profile_map

api_profile_bp = Blueprint('api_profile', __name__, url_prefix='/api/profile')

@api_profile_bp.route('/detail/<int:profile_id>', methods=['GET'])
def get_profile_detail(profile_id):
    """提供完整 profile 詳細內容"""
    profile = profile_map.get(profile_id)
    if profile:
        return Response(
            json.dumps(profile, ensure_ascii=False, indent=2),
            content_type='application/json'
        )
    else:
        return Response(
            json.dumps({"error": f"找不到 ID 為 {profile_id} 的角色"}, ensure_ascii=False, indent=2),
            status=404,
            content_type='application/json'
        )