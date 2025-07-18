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

edit_bp = Blueprint('edit_bp', __name__)

def ensure_general_data_updated(character_entry: CharacterFileEntry) -> None:
    character_data = character_entry.get_character_data()
    global_general = get_global_general_data()
    global_version = global_general.get('!version', -1)

    character_general = character_data.get_value(["story", "general"])
    character_version = character_general.get('!version', -1) if isinstance(character_general, dict) else -1

    if not isinstance(character_general, dict) or character_version < global_version:
        if "story" not in character_data.get_data():
            character_data.get_data()["story"] = {}

        character_data.get_data()["story"]["general"] = global_general
        character_data.global_data = global_general
        character_entry.general_version = global_version
        character_entry.set_sync_flag(True)

def ensure_profile_data_updated(character_entry: CharacterFileEntry) -> None:
    if character_entry.profile_id is None:
        return

    global_profile_data = get_profile(character_entry.profile_id)
    global_profile_version = global_profile_data.get('!version', -1)

    character_data = character_entry.get_character_data()
    character_profile_data = character_data.get_value(["story", "profile"])
    character_profile_version = character_entry.profile_version

    if not isinstance(character_profile_data, dict) or character_profile_version < global_profile_version:
        data = character_data.get_data()

        # 確保 "story" 存在
        if "story" not in data:
            data["story"] = {}

        # 直接更新 profile 區塊（不透過 set_value）
        data["story"]["profile"] = global_profile_data.copy()

        # 更新 character_entry 的 profile 狀態
        character_entry.profile_id = global_profile_data.get("!id", character_entry.profile_id)
        character_entry.profile_version = global_profile_version

        character_entry.set_sync_flag(True)

def reload_character_data(scan_path: str, character_id: str) -> [Dict[str, Any], tuple]:
    """
    重新讀取角色圖檔並解析，更新共享資料庫，並確保 general 資料是最新。
    成功回傳 character_data.get_data()。
    發生錯誤時回傳 (jsonify響應, status_code) tuple。
    """
    try:
        add_or_update_character_with_path(scan_path, character_id)

        character_file_entry_obj = get_character_file_entry(character_id)
        if not character_file_entry_obj:
            return jsonify({"error": f"雖然成功讀取檔案，但解析後仍無法取得角色數據: {character_id}。"}), 500

        ensure_general_data_updated(character_file_entry_obj)
        ensure_profile_data_updated(character_file_entry_obj)

        character_data_obj = character_file_entry_obj.get_character_data()
        return character_data_obj.get_data()

    except FileNotFoundError:
        return jsonify({"error": "檔案不存在。", "parsed_data_preview": "無"}), 404
    except Exception as e:
        return jsonify({"error": f"讀取角色檔案時發生錯誤: {e}"}), 500


@edit_bp.route('/edit')
def edit():
    character_id = request.args.get('character_id')
    if not character_id:
        return "缺少角色 ID。", 400

    try:
        character_file_entry_obj = get_character_file_entry(character_id)

        if not character_file_entry_obj:
            print(f"ℹ️ 共享資料庫中未找到 '{character_id}'，嘗試從檔案讀取並處理。")
            scan_path = current_app.config['SCAN_PATH']
            processed_result = reload_character_data(scan_path, character_id)

            if isinstance(processed_result, tuple) and len(processed_result) == 2:
                # 錯誤 jsonify 響應
                return processed_result

            character_file_entry_obj = get_character_file_entry(character_id)
            if not character_file_entry_obj:
                return f"處理檔案成功，但未能從數據庫獲取 CharacterFileEntry: {character_id}。", 500

        # 確保 general 區塊是最新（保險起見）
        ensure_general_data_updated(character_file_entry_obj)
        ensure_profile_data_updated(character_file_entry_obj)

        content_for_frontend = character_file_entry_obj.get_character_data().get_data()
        session['current_edit_character_id'] = character_id
        return render_template('edit.html', character_id=character_id, data=json.dumps(content_for_frontend))

    except Exception as e:
        return f"內部錯誤: {e}", 500      
 