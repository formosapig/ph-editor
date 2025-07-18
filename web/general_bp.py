# ph-editor/web/general_bp.py

from flask import Blueprint, request, render_template, jsonify, current_app, session, Response
import os
import json
import base64
import traceback
from typing import Dict, Any

# get_character_data 會處理延遲解析邏輯
from core.shared_data import (
    get_character_file_entry,
    get_character_data,
    
    add_or_update_character_with_path,
    get_global_general_data,
    get_profile,
)
from core.character_file_entry import CharacterFileEntry

general_bp = Blueprint('general_bp', __name__)

@general_bp.route('/general')
def general():
    general_data = get_global_general_data()
    color_traits_data = general_data['color_traits']
    tag_type_setting_data = general_data['tag_type_setting']
    tag_data = general_data['tag']
    

    return render_template(
        'general.html',
        color_traits=color_traits_data,
        tag_type_setting=tag_type_setting_data,
        tag_list=tag_data)