# ph-editor/api/character.py

from flask import Blueprint, request, jsonify, current_app, session, Response
import json
from typing import Dict, Any, Union, Tuple

from core.shared_data import (
    get_character_data,
    get_character_file_entry,
    add_or_update_character_with_path,
    get_global_general_data,
    characters_db,
    characters_db_lock,
    update_global_general_data,
)
from core.character_file_entry import CharacterFileEntry

api_character_bp = Blueprint('api_character', __name__, url_prefix='/api/character')

def ensure_general_data_updated(character_entry: CharacterFileEntry) -> None:
    character_data = character_entry.get_character_data()
    global_general = get_global_general_data()
    global_version = global_general.get('!version', -1)

    character_general = character_data.get_value(["story", "general"])
    character_version = character_general.get('!version', -1) if isinstance(character_general, dict) else -1

    if not isinstance(character_general, dict) or character_version < global_version:
        data = character_data.get_data()
        if "story" not in data:
            data["story"] = {}

        data["story"]["general"] = global_general
        character_data.global_data = global_general
        character_entry.general_version = global_version
        character_entry.set_save_flag(True)

def reload_character_data(scan_path: str, character_id: str) -> Union[Dict[str, Any], Tuple]:
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

        character_data_obj = character_file_entry_obj.get_character_data()
        return character_data_obj.get_data()

    except FileNotFoundError:
        return jsonify({"error": "檔案不存在。", "parsed_data_preview": "無"}), 404
    except Exception as e:
        return jsonify({"error": f"讀取角色檔案時發生錯誤: {e}"}), 500


@api_character_bp.route('/reload', methods=['GET'])
def reload_file():
    try:
        character_id = session.get('current_edit_character_id')
        if not character_id:
            return jsonify({'error': '尚未載入角色或會話數據丟失，請先載入角色。'}), 400

        scan_path = current_app.config['SCAN_PATH']
        processed_result = reload_character_data(scan_path, character_id)

        # 如果是錯誤回傳（tuple）直接回應
        if isinstance(processed_result, tuple) and len(processed_result) == 2:
            return processed_result

        return Response(
            json.dumps(processed_result, ensure_ascii=False, indent=2),
            content_type='application/json'
        )

    except Exception as e:
        return jsonify({'error': f'內部錯誤: {e}'}), 500


@api_character_bp.route('/save', methods=['POST'])
def save_file():
    """
    從 session 拿 character_id，呼叫 CharacterFileEntry.save() 來存檔。
    處理並回傳各類異常訊息。
    """
    character_id = session.get('current_edit_character_id')
    if not character_id:
        return jsonify({'error': '會話中沒有角色 ID，請重新載入角色。'}), 400

    entry = get_character_file_entry(character_id)
    if not entry:
        return jsonify({'error': f'找不到角色資料：{character_id}，請重新載入檔案。'}), 404

    try:
        entry.save()
        return jsonify({'success': True, 'message': '角色資料已成功保存！'})

    except FileNotFoundError as e:
        return jsonify({'error': f'檔案不存在：{str(e)}'}), 404
    except ValueError as e:
        return jsonify({'error': f'資料格式錯誤：{str(e)}'}), 400
    except IOError as e:
        return jsonify({'error': f'寫入檔案失敗：{str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'發生未知錯誤：{str(e)}'}), 500

@api_character_bp.route('/ping_pong_save', methods=['POST'])
def ping_pong_save():
    """
    掃描 characters_db 找第一個 save_flag 為 True 的角色，呼叫其 save() 儲存。
    回傳成功或錯誤 JSON。
    """
    saved_character_id: Optional[str] = None

    try:
        with characters_db_lock:
            for character_id, character_file_entry in characters_db.items():
                if character_file_entry.needs_saving():
                    character_file_entry.save()
                    character_file_entry.set_save_flag(False)
                    saved_character_id = character_id
                    break

        if saved_character_id:
            return jsonify({
                "success": True,
                "message": f"成功儲存角色: {saved_character_id}",
                "character_id": saved_character_id
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "沒有找到待儲存的角色。",
                "character_id": None
            }), 200

    except FileNotFoundError as e:
        return jsonify({"error": f"檔案不存在: {str(e)}"}), 404
    except ValueError as e:
        return jsonify({"error": f"資料格式錯誤: {str(e)}"}), 400
    except IOError as e:
        return jsonify({"error": f"寫入檔案失敗: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"發生未知錯誤: {str(e)}"}), 500
        
@api_character_bp.route('/update/<main_tab>/<sub_tab>', methods=['PUT'])
def update_data(main_tab, sub_tab):
    """
    更新當前角色 parsed_data 指定節點：
    URL 參數提供 main_tab 和 sub_tab，
    JSON body 提供要更新的 data。
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': '請求內容必須是 JSON 格式。'}), 400

    new_data = data.get('data')
    if new_data is None:
        return jsonify({'error': '缺少 data 欄位。'}), 400

    character_id = session.get('current_edit_character_id')
    if not character_id:
        return jsonify({'error': '會話中無角色ID，請先載入角色。'}), 400

    character_data_obj = get_character_data(character_id)
    if not character_data_obj:
        return jsonify({'error': f'找不到角色數據: {character_id}。請重新載入檔案。'}), 404

    try:
        # 若 main_tab 不存在，建立空 dict
        if main_tab not in character_data_obj.parsed_data:
            character_data_obj.parsed_data[main_tab] = {}

        # 更新子節點
        character_data_obj.parsed_data[main_tab][sub_tab] = new_data
        
        response_data = {
            'success': True,
            'message': f'角色資料節點 [{main_tab}][{sub_tab}] 更新成功（尚未寫入檔案）。'
        }

        # 全域資料檢查...
        if main_tab == 'story' and sub_tab == 'general':
            update_global_general_data(new_data, increment_version=True)
            # 回傳新版版本號給前端
            updated_version = new_data.get('!version', None)
            response_data['global_version_updated'] = True

        return jsonify(response_data)

    except Exception as e:
        import traceback
        traceback.print_exc()  # 會印出錯誤堆疊
        return jsonify({'error': f'更新失敗: {str(e)}'}), 500