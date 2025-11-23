# ph-editor/compare/basic_compare.py
from typing import Dict, Any

from utils.utils import get_nested_value

BASIC_KEY_NAME_MAP = {
    #"file_id": "檔案",
    #"remark": "註解",
    "profile": "角色",
    "age": "年齡",
    "tag": "標籤",
    "persona": "外顯",
    "shadow": "內隱",
    "title": "場景",
    "pilot": "劇情",
    "notes": "備註",
}

BASIC_KEY_BLOCK_MAP = {key: 'basic' for key in BASIC_KEY_NAME_MAP}

def flatten_basic_data(d: Dict[str, Any]) -> Dict[str, Any]:
    result = {}
    
    # profile ?!
    result["profile"] = get_nested_value(d, "story.profile.name", "")
    result["tag"] = get_nested_value(d, "story.backstage.tag", "")
    
    # calculate age
    year_val = get_nested_value(d, "story.scenario.year", -1)
    born_val = get_nested_value(d, "story.profile.born", -1)
    result["age"] = year_val - born_val if year_val != -1 and born_val != -1 else ""
    
    result["persona"] = get_nested_value(d, "story.backstage.persona", "")
    result["shadow"] = get_nested_value(d, "story.backstage.shadow", "")
    
    title = get_nested_value(d, "story.scenario.title", "")
    subtitle = get_nested_value(d, "story.backstage.subtitle", "")
    if title != "":
        result["title"] = "🎬" + title
        if subtitle != "":
            result["title"] += "-" + subtitle
    else:
        result["title"] = ""
        
    result["pilot"] = get_nested_value(d, "story.scenario.pilot", "")
    
    # 備註們...
    # (Emoji 1, 路徑), (Emoji 2, 路徑), (Emoji 3, 路徑)
    note_sources = [
        ("👤️", "story.profile.notes"),
        ("🎬️", "story.scenario.notes"),
        ("📜", "story.backstage.notes")
    ]
    
    filtered_notes = [
        f"{emoji}{note}"
        for emoji, path in note_sources
        if (note := get_nested_value(d, path, "")) # 使用海象運算子 (:=) 取得值並同時檢查
    ]
    
    result["notes"] = "\n".join(filtered_notes)
    
    
    return result