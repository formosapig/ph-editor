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
    result["title"] = "🎬" + title if title != "" else ""
    result["pilot"] = get_nested_value(d, "story.scenario.pilot", "")
    
    notes = [
        get_nested_value(d, "story.profile.notes", ""),
        get_nested_value(d, "story.scenario.notes", ""),
        get_nested_value(d, "story.backstage.notes", "")
    ]
    filtered_notes = [f"⚙️{n}" for n in notes if n]
    result["notes"] = "\n".join(filtered_notes)
    return result