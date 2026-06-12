# ph-editor/api/character_bp.py
import json
import logging
import os
from flask import Blueprint, Response, current_app, jsonify, request
from send2trash import send2trash
from core.shared_data import (
    get_character_file_entry,
    get_processed_metadata_list,
    remove_character_file_entry,
)
from utils.character_file_utils import reload_character_data
from utils.decorators import require_json_data, require_scan_path

logger = logging.getLogger(__name__)


api_characters_bp = Blueprint("api_characters", __name__, url_prefix="/api/characters")


@api_characters_bp.get("")
def get_characters():
    # 從 query string 獲取 profile_id，例如 /api/characters?profile_id=18
    profile_id = request.args.get("profile_id", type=int)
    
    if profile_id is None:
        raise FileNotFoundError()

    # 呼叫你定義好的計算函式
    results = get_processed_metadata_list(profile_id)
    
    return jsonify({"results": results})


@api_characters_bp.delete("")
@require_scan_path
def bulk_delete_characters(scan_path):
    """
    get sns from json object and remove then all. return success removed sns...
    """
    data = request.get_json()
    serial_numbers_to_delete = data.get("serial_numbers", [])  # 改為接收多個檔名（list）
    if not serial_numbers_to_delete or not isinstance(serial_numbers_to_delete, list):
        return jsonify({"status": "error", "message": "未提供檔案清單或格式錯誤"}), 400

    results = []
    for sn in serial_numbers_to_delete:
        entry = get_character_file_entry(sn)
        if not entry:
            results.append({"sn": sn, "status": "角色資料不存在"})
            continue

        full_path_original = os.path.join(scan_path, f"{entry.file_id}.png")
        logger.debug(f"Delete {full_path_original}")
        try:
            if os.path.exists(full_path_original):
                # os.remove(full_path_original) 太兇殘了.
                send2trash(full_path_original)
                logger.info(f"刪除原始檔案: {full_path_original}")
                remove_character_file_entry(sn)
                results.append({"sn": sn, "status": "success"})
            else:
                results.append({"sn": sn, "status": "file not found"})
        except Exception as e:
            results.append(
                {"sn": sn, "status": "error", "message": str(e)}
            )

    return jsonify({"results": results})


@api_characters_bp.delete("/upstream")
@require_json_data
def patch_character_upstream(data):
    # 預期 data 格式: {"sn_list": ["sn1", "sn2", ...]}
    sn_list = data.get("sn_list", [])
    
    if not sn_list:
        return jsonify({
            "success": False,
            "message": "未提供任何角色 SN。",
        })
    
    success_count = 0
    failed_sn_list = []
    
    for sn in sn_list:
        # 根據 sn 取得 entry 物件
        entry = get_character_file_entry(sn)
        
        if not entry:
            failed_sn_list.append(sn)
            continue
        
        entry.update_upstream_sn("")
    
    if failed_sn_list:
        return jsonify({
            "success": False,
            "message": f"部分角色更新失敗，失敗 SN: {failed_sn_list}"
        })
    
    return jsonify({
        "success": True,
        "message": f"成功刪除 {success_count} 個角色的 upstream_sn。",
    })


@api_characters_bp.route("/reload", methods=["GET"])
def reload_file():
    file_id = request.args.get('file_id')
    if not file_id:
        return jsonify({'error': '缺少 file_id'}), 400
        
    try:
        scan_path = current_app.config["SCAN_PATH"]
        processed_result = reload_character_data(scan_path, file_id)

        # 如果是錯誤回傳（tuple）直接回應
        if isinstance(processed_result, tuple) and len(processed_result) == 2:
            return processed_result

        return Response(
            json.dumps(processed_result, ensure_ascii=False, indent=2),
            content_type="application/json",
        )

    except Exception as e:
        return jsonify({"error": f"內部錯誤: {e}"}), 500
   

@api_characters_bp.route("/save", methods=["POST"])
def save_file():
    """ 由前端傳來 fild_id 進行儲存 """
    data = request.get_json()
    file_id = data.get('file_id')
    
    if not file_id:
        return jsonify({'error': '缺少 file_id'}), 400

    entry = get_character_file_entry(file_id)
    if not entry:
        return (
            jsonify({"error": f"找不到角色資料：{file_id}，請重新載入檔案。"}),
            404,
        )

    try:
        entry.save(True)  # individual save only.
        return jsonify({"success": True, "message": "角色資料已成功保存！"})

    except FileNotFoundError as e:
        return jsonify({"error": f"檔案不存在：{str(e)}"}), 404
    except ValueError as e:
        return jsonify({"error": f"資料格式錯誤：{str(e)}"}), 400
    except IOError as e:
        return jsonify({"error": f"寫入檔案失敗：{str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"發生未知錯誤：{str(e)}"}), 500