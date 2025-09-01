import traceback
from flask import (
    Blueprint,
    current_app,
    jsonify,
    render_template,
    request,
)

# 確保這裡有導入 get_character_file_entry
from core.shared_data import get_character_file_entry
# all compares
from compare.basic_compare import (
    BASIC_KEY_NAME_MAP,
    BASIC_KEY_BLOCK_MAP,
    flatten_basic_data,
)

from compare.hair_compare import (
    HAIR_KEY_NAME_MAP,
    HAIR_KEY_BLOCK_MAP,
    flatten_hair_data,
)

from compare.face_compare import (
    FACE_KEY_NAME_MAP,
    FACE_KEY_BLOCK_MAP,
    flatten_face_data,
)

from compare.body_compare import (
    BODY_KEY_NAME_MAP,
    BODY_KEY_BLOCK_MAP,
    flatten_body_data,
)

from compare.clothing_compare import (
    CLOTHING_KEY_NAME_MAP,
    CLOTHING_KEY_BLOCK_MAP,
    flatten_clothing_data,
)

from compare.accessory_compare import (
    ACCESSORY_KEY_NAME_MAP,
    ACCESSORY_KEY_BLOCK_MAP,
    flatten_accessory_data,
)

import random
import string
import json
import logging
from collections import defaultdict 

logger = logging.getLogger(__name__)
logger.disabled = True

compare_bp = Blueprint("compare_bp", __name__)

@compare_bp.route("/compare")
def compare():
    file_ids_str = request.args.get("files")
    
    selected_characters_processed = []

    if file_ids_str:
        file_ids = [f.strip() for f in file_ids_str.split(',') if f.strip()]

        for file_id in file_ids:
            try:
                logger.debug(f"轉換 {file_id} 的資料。")
                character_entry = get_character_file_entry(file_id)

                if character_entry is None:
                    logger.debug(f"檔案 ID: {file_id} 的 character_entry 不存在，跳過轉換。")
                    continue

                if not hasattr(character_entry, 'character_data'):
                    logger.debug(f"檔案 ID: {file_id} 的 character_entry 沒有 'character_data' 屬性，跳過轉換。")
                    continue

                full_character_data = character_entry.get_character_data()

                if not isinstance(full_character_data, dict):
                    logger.debug(f"檔案 ID: {file_id} 的 character_data 不是字典類型，而是 {type(full_character_data).__name__}，跳過轉換。")
                    continue

                logger.debug(f"檔案 ID: {file_id} 的所有資料檢查通過，開始進行轉換處理。")

                final_flat_data = {}
                final_flat_data['file_id'] = file_id
                final_flat_data['remark'] = character_entry.get_remark()
                
                # 依次合併
                final_flat_data.update(flatten_basic_data(full_character_data))
                final_flat_data.update(flatten_hair_data(full_character_data))
                final_flat_data.update(flatten_face_data(full_character_data))
                final_flat_data.update(flatten_body_data(full_character_data))
                final_flat_data.update(flatten_clothing_data(full_character_data))
                final_flat_data.update(flatten_accessory_data(full_character_data))

                selected_characters_processed.append(final_flat_data)

            except Exception as e:
                # 這裡假設你的 logger 來自 Flask 的 current_app.logger
                # 如果是獨立的 logger，直接用 logger.error 即可
                logger.error(f"處理 file_id: {file_id} 時發生錯誤: {e}\n{traceback.format_exc()}")
                selected_characters_processed.append({"file_id": file_id, "error": f"資料載入失敗: {e}"})

    # 將 attribute_name_map 的所有 key 依序抽出，填入 attributes_list
    ALL_KEY_NAME_MAP = {}
    ALL_KEY_NAME_MAP.update(BASIC_KEY_NAME_MAP)
    ALL_KEY_NAME_MAP.update(HAIR_KEY_NAME_MAP)
    ALL_KEY_NAME_MAP.update(FACE_KEY_NAME_MAP)
    ALL_KEY_NAME_MAP.update(BODY_KEY_NAME_MAP)
    ALL_KEY_NAME_MAP.update(CLOTHING_KEY_NAME_MAP)
    ALL_KEY_NAME_MAP.update(ACCESSORY_KEY_NAME_MAP)
    
    ALL_KEY_BLOCK_MAP = {}
    ALL_KEY_BLOCK_MAP.update(BASIC_KEY_BLOCK_MAP)
    ALL_KEY_BLOCK_MAP.update(HAIR_KEY_BLOCK_MAP)
    ALL_KEY_BLOCK_MAP.update(FACE_KEY_BLOCK_MAP)
    ALL_KEY_BLOCK_MAP.update(BODY_KEY_BLOCK_MAP)
    ALL_KEY_BLOCK_MAP.update(CLOTHING_KEY_BLOCK_MAP)
    ALL_KEY_BLOCK_MAP.update(ACCESSORY_KEY_BLOCK_MAP)
        
    attributes_list = list(ALL_KEY_NAME_MAP.keys())

    # 將處理後的數據傳遞給模板
    return render_template(
        'compare.html',
        characters=selected_characters_processed,
        attributes=attributes_list,
        attribute_name_map=ALL_KEY_NAME_MAP,
        attribute_block_map=ALL_KEY_BLOCK_MAP,
    )

@compare_bp.route("/compare/reload")
def compare_reload():
    file_id = request.args.get("file_id")
    
    if not file_id:
        return jsonify({"error": "file_id missing"}), 400
    
    try:
        logger.debug(f"轉換 {file_id} 的資料。")
        character_entry = get_character_file_entry(file_id)

        if character_entry is None:
            logger.debug(f"檔案 ID: {file_id} 的 character_entry 不存在。")
            return jsonify({"error": "file not found"}), 404

        if not hasattr(character_entry, 'character_data'):
            logger.debug(f"檔案 ID: {file_id} 的 character_entry 沒有 'character_data' 屬性。")
            return jsonify({"error": "invalid character data"}), 400

        full_character_data = character_entry.get_character_data()

        if not isinstance(full_character_data, dict):
            logger.debug(f"檔案 ID: {file_id} 的 character_data 不是字典類型，而是 {type(full_character_data).__name__}")
            return jsonify({"error": "character data is not dict"}), 400

        logger.debug(f"檔案 ID: {file_id} 的所有資料檢查通過，開始進行轉換處理。")

        final_flat_data = {'file_id': file_id}
        final_flat_data.update({'remark': character_entry.get_remark()})
                
        # 依次合併
        final_flat_data.update(flatten_basic_data(full_character_data))
        final_flat_data.update(flatten_hair_data(full_character_data))
        final_flat_data.update(flatten_face_data(full_character_data))
        final_flat_data.update(flatten_body_data(full_character_data))
        final_flat_data.update(flatten_clothing_data(full_character_data))
        final_flat_data.update(flatten_accessory_data(full_character_data))

    except Exception as e:
        logger.error(f"處理 file_id: {file_id} 時發生錯誤: {e}\n{traceback.format_exc()}")
        return jsonify({"error": f"資料載入失敗: {e}"}), 500

    # 回傳 JSON
    return jsonify(final_flat_data)