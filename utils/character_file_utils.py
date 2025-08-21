# ph-editor/utils/character_file_utils.py
import json
import logging
from typing import Any, Dict, Tuple, Union

#from core.character_file_entry import CharacterFileEntry
# get_character_data 會處理延遲解析邏輯
from core.shared_data import (
    add_or_update_character_with_path,
    get_character_file_entry,
    get_general_data,
)

def reload_character_data(
    scan_path: str, file_id: str
) -> Union[Dict[str, Any], Tuple]:
    """
    重新讀取角色圖檔並解析，更新共享資料庫，並確保 general 資料是最新。
    成功回傳 character_data.get_data() + genenarl_data...。
    發生錯誤時回傳 (jsonify響應, status_code) tuple。
    """
    try:
        add_or_update_character_with_path(scan_path, file_id)

        character_file_entry_obj = get_character_file_entry(file_id)
        if not character_file_entry_obj:
            return (
                jsonify(
                    {
                        "error": f"雖然成功讀取檔案，但解析後仍無法取得角色數據: {file_id}。"
                    }
                ),
                500,
            )

        result = character_file_entry_obj.get_character_data()
        
        # 附加 general_data
        if "story" not in result:
            result["story"] = {}

        result["story"]["general"] = get_general_data()
        
        return result

    except FileNotFoundError:
        return jsonify({"error": "檔案不存在。", "parsed_data_preview": "無"}), 404
    except Exception as e:
        return jsonify({"error": f"讀取角色檔案時發生錯誤: {e}"}), 500


def append_general_data(data: Dict[str, Any]):
    # 附加 general_data
    if "story" not in data:
        data["story"] = {}

    data["story"]["general"] = get_general_data()
