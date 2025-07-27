import logging
import traceback
from typing import List, Dict, Any, Tuple, Set, Optional, Union
from .shared_data import get_character_file_entry
from compare.basic import BASIC_KEY_NAME_MAP, flatten_basic_data

logger = logging.getLogger(__name__) # 這裡使用一個普通的 logger，或者你可以傳入 Flask 的 current_app.logger

# 將你的核心處理邏輯封裝成一個函式
def process_selected_files(
    file_ids_str: Optional[str]
) -> Tuple[List[Dict[str, Any]], List[str], Dict[str, str]]:
    """
    處理選定的檔案 ID 字串，轉換為前端表格所需的格式。

    Args:
        file_ids_str: 包含檔案 ID 的逗號分隔字串，來自 request.args.get("files")。

    Returns:
        一個元組，包含：
        - selected_characters_processed: 處理後的角色資料列表。
        - final_attributes_list: 所有唯一屬性的列表，用於表頭順序。
        - attribute_name_map: 屬性名稱到顯示名稱的映射字典。
    """
    selected_characters_processed = []
    all_unique_attributes: Set[str] = set() # 用來收集所有角色的唯一屬性名稱

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

                if not isinstance(character_entry.character_data.parsed_data, dict):
                    logger.debug(f"檔案 ID: {file_id} 的 character_data.parsed_data 不是字典類型，而是 {type(character_entry.character_data.parsed_data).__name__}，跳過轉換。")
                    continue

                logger.debug(f"檔案 ID: {file_id} 的所有資料檢查通過，開始進行轉換處理。")

                raw_character_data = character_entry.character_data.parsed_data
                final_flat_data = {}
                final_flat_data['file_id'] = file_id
                
                # 依次合併
                final_flat_data.update(flatten_basic_data(raw_character_data))

                selected_characters_processed.append(final_flat_data)

            except Exception as e:
                # 這裡假設你的 logger 來自 Flask 的 current_app.logger
                # 如果是獨立的 logger，直接用 logger.error 即可
                logger.error(f"處理 file_id: {file_id} 時發生錯誤: {e}\n{traceback.format_exc()}")
                selected_characters_processed.append({"file_id": file_id, "error": f"資料載入失敗: {e}"})
                all_unique_attributes.add("error")

    # 將 attribute_name_map 的所有 key 依序抽出，填入 attributes_list
    ALL_KEY_NAME_MAP = {}
    ALL_KEY_NAME_MAP.update(BASIC_KEY_NAME_MAP)
    
    attributes_list = list(ALL_KEY_NAME_MAP.keys())

    return selected_characters_processed, attributes_list, ALL_KEY_NAME_MAP

