# ph-editor/web/edit_bp.py
from collections import Counter, OrderedDict
import json
import logging
import re
from flask import (
    Blueprint,
    jsonify,
    render_template,
)

# get_character_data 會處理延遲解析邏輯
from core.shared_data import (
    #find_another_sn_by_scenario_id,
    get_general_data,
    get_info_by_tag_id,
    prepare_mistor_data,
)
from utils.character_file_utils import (
    #reload_character_data,
    append_general_data,
)
from utils.decorators import inject_character_file_entry, require_json_data
from utils.input_key import execute_snapshot
from utils.utils import hex_to_hsv
from web.extensions import cache

edit_bp = Blueprint("edit_bp", __name__)


logger = logging.getLogger(__name__)
#logger.disabled = True


def _add_list_prefix(text):
    """對不是以 # { [ 開頭的行，加上 '- ' 前綴"""
    if not text:
        return text
    lines = text.split('\n')
    processed = []
    for line in lines:
        stripped = line.lstrip()
        if stripped and stripped[0] not in '#{[':
            processed.append(f'  {line}')
        else:
            processed.append(line)
    return '\n'.join(processed)

def _merge_with_cancel(*sections):
    """
    sections: 每個是 (source_name, text) 或直接 text
    這裡簡化：直接傳入 text 字串 list
    """
    lines = []
    for text in sections:
        if text:
            lines.extend(text.splitlines())

    #logger.error(f"lines = ${lines}")

    counter = Counter()
    # 如果要保留順序，用 OrderedDict 存首次出現
    order = OrderedDict()
    other_lines = []
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- "):
            item = stripped[2:]
            counter[item] += 1
            if item not in order:
                order[item] = None
        elif stripped.startswith("x "):
            item = stripped[2:]
            counter[item] -= 1
            if item not in order:
                order[item] = None
        else:
            other_lines.append(line)  # 普通行直接保留
    
    # 保留淨值 >0 的項目，按首次出現順序
    result_items = []
    for item in order:
        if counter[item] > 0:
            result_items.append(f"- {item}")

    #logger.error(f"lines = ${result_items}")
    #logger.error(f"lines = ${other_lines}")
    
    # 普通行放在最後（或可穿插，依需求）
    return "\n".join(result_items + other_lines)

def _merge_with_override(*texts):
    """
    合併多個文字來源，對於 key : value 格式，後者取代前者
    非 key : value 格式的行則直接保留
    """
    import re
    
    # 收集所有行
    all_lines = []
    for text in texts:
        if text:
            all_lines.extend(text.splitlines())
    
    # 用來儲存最終的 key-value 對
    kv_dict = {}
    # 用來儲存非 key-value 格式的行（保留順序）
    other_lines = []
    
    # 用來記錄 key 出現的順序
    key_order = []
    key_set = set()
    
    for line in all_lines:
        stripped = line.strip()
        # 匹配 key : value 格式（允許前後有空白）
        match = re.match(r'^([^:]+)\s*:\s*(.+)$', stripped)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()
            
            # 如果是新的 key，記錄順序
            if key not in key_set:
                key_set.add(key)
                key_order.append(key)
            
            # 後者取代前者（直接覆蓋）
            kv_dict[key] = value
        else:
            # 非 key-value 格式的行直接保留
            other_lines.append(line)
    
    # 按照順序輸出 key-value 行
    result_lines = []
    for key in key_order:
        if key in kv_dict:
            result_lines.append(f"{key} : {kv_dict[key]}")
    
    # 加上其他非 key-value 格式的行
    result_lines.extend(other_lines)
    
    return "\n".join(result_lines)

def _build_final_data(info, persona_name, persona_code, shadow_name, shadow_code, profile, scenario, backstage):
    """
    建構 final_data，將四個來源的資料合併
    
    Args:
        info: info 資料
        persona_code: 外顯顏色代碼 (hex)
        shadow_code: 內隱顏色代碼 (hex)
        profile: profile 資料
        scenario: scenario 資料
        backstage: backstage 資料
    
    Returns:
        dict: 包含 soul, meat, form, code 的字典
    """
    final_data = {}
    
    # 轉換顏色代碼
    persona_hsv = hex_to_hsv(persona_code)
    shadow_hsv = hex_to_hsv(shadow_code)
    
    # 建立顯示文字（只有當轉換成功時才顯示）
    persona_display = f"外顯 : {persona_name} {persona_hsv}" if persona_name and persona_hsv else ""
    shadow_display = f"內隱 : {shadow_name} {shadow_hsv}" if shadow_name and shadow_hsv else ""
    
    # 合併外顯和內隱
    color_display = ""
    if persona_display and shadow_display:
        color_display = f"{persona_display}\n{shadow_display}"
    elif persona_display:
        color_display = persona_display
    elif shadow_display:
        color_display = shadow_display
    
    for key in ["soul", "meat", "form", "code"]:
        i = info.get(key)
        p = profile.get(key)
        s = scenario.get(key)
        b = backstage.get(key)
        
        # 只有 form 套用抵消邏輯，並在最前面插入顏色顯示
        if key == "form":
            merged = _merge_with_cancel(p, s, i, b)
            # 如果有顏色顯示，插入到最前面
            if color_display:
                final_data[key] = f"{color_display}\n{merged}" if merged else color_display
            else:
                final_data[key] = merged
                
        elif key == "code":
            final_data[key] = _merge_with_override(p, s, i, b)    
        else:
            parts = []
            if i: parts.append(i)
            if p: parts.append(f"# 簡介限定\n{p}")
            if s: parts.append(f"# 場景限定\n{s}")
            if b: parts.append(f"# 幕後限定\n{b}")
            final_data[key] = "\n".join(parts)
    
    return final_data

@edit_bp.get("/edit/<sn>")
@inject_character_file_entry
def edit(sn, entry):
    """
    處理編輯角色的頁面請求。
    """
    result_content = entry.get_character_data()
    append_general_data(result_content)

    #sub_sn = find_another_sn_by_scenario_id(entry.scenario_id, sn)
    correct = entry.get_correct()[1]
    info = get_info_by_tag_id(entry.tag_id)
    persona_name = entry.get_persona_name()
    persona_code = entry.get_persona_code()
    shadow_name = entry.get_shadow_name()
    shadow_code = entry.get_shadow_code()
    profile = entry.get_profile()
    scenario = entry.get_scenario()
    backstage = entry.get_backstage()
    
    final_data = _build_final_data(info, persona_name, persona_code, shadow_name, shadow_code, profile, scenario, backstage)

    # 混淆
    cached_data = cache.get('mistor')
    
    if cached_data is None:
        mistor_map, mistor_regex = prepare_mistor_data()
        cached_data = {
            'mistor_map': json.dumps(mistor_map, ensure_ascii=False),
            'mistor_regex': mistor_regex
        }
        # 存入快取，設定過期時間（例如 300 秒 / 5 分鐘）
        cache.set('mistor', cached_data, timeout=699)
    
    return render_template(
        "edit.html",
        sn=sn,
        #sub_sn=sub_sn,  # sub file 我們並不編輯它，只秀截圖
        file_id=entry.file_id,
        remark=entry.get_remark(),
        correct=correct,
        soul=final_data["soul"],
        meat=final_data["meat"],
        form=final_data["form"],
        code=final_data["code"],
        mistor_map=cached_data["mistor_map"],
        mistor_regex=cached_data["mistor_regex"],
        data=json.dumps(result_content), # 注意, 如果丟 dict 去前端, json 的 key 會跑掉
    )


@edit_bp.patch("/edit/<sn>")
@inject_character_file_entry
def patch_data(sn, entry):
    """
    處理編輯角色的頁面請求。
    """
    # 特別重新讀取二進制資料
    entry.reload_binary()
    result_content = entry.get_character_data()
    append_general_data(result_content)

    #sub_sn = find_another_sn_by_scenario_id(entry.scenario_id, sn)
    correct = entry.get_correct()[1]
    info = get_info_by_tag_id(entry.tag_id)
    persona_name = entry.get_persona_name()
    persona_code = entry.get_persona_code()
    shadow_name = entry.get_shadow_name()
    shadow_code = entry.get_shadow_code()
    profile = entry.get_profile()
    scenario = entry.get_scenario()
    backstage = entry.get_backstage()

    final_data = _build_final_data(info, persona_name, persona_code, shadow_name, shadow_code, profile, scenario, backstage)

    # 混淆資料不重讀...

    return jsonify({
        "file_id": entry.file_id,
        "correct": correct,
        "soul": final_data["soul"],
        "meat": final_data["meat"],
        "form": final_data["form"],
        "code": final_data["code"],
        "data": result_content
    })

@edit_bp.post("/edit/snapshot")
@require_json_data
def input_key_for_snapshot(data):
    """
    處理編輯角色的頁面請求。
    """
    input = data.get('input')
    log = execute_snapshot(input)

    return jsonify({
        "log" : log
    })