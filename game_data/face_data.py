# your_character_project/game_data/face_data.py

FACE_DETAILS = {
    # 輪廓
    'contour': [
        {'id': 0, 'name': {'ja': 'ヘッドA01', 'zh': '頭A01'}},
        {'id': 2, 'name': {'ja': 'ヘッドA02', 'zh': '頭A02'}},
        {'id': 3, 'name': {'ja': 'ヘッドA03', 'zh': '頭A03'}},
        {'id': 1, 'name': {'ja': 'ヘッドB', 'zh': '頭B'}},
    ],
    # 肌肉
    'muscle': [
        {'id': 500, 'name': {'ja': 'PH タイプ01', 'zh': 'PH 類型01'}},
        {'id': 2, 'name': {'ja': 'PH タイプ02', 'zh': 'PH 類型02'}},
        {'id': 3, 'name': {'ja': 'PH タイプ03', 'zh': 'PH 類型03'}},
        {'id': 4, 'name': {'ja': 'PH タイプ04', 'zh': 'PH 類型04'}},
        {'id': 5, 'name': {'ja': 'PH タイプ05', 'zh': 'PH 類型05'}},
        {'id': 6, 'name': {'ja': 'PH タイプ06', 'zh': 'PH 類型06'}},
        {'id': 7, 'name': {'ja': 'PH タイプ07', 'zh': 'PH 類型07'}},
        {'id': 8, 'name': {'ja': 'PH タイプ08', 'zh': 'PH 類型08'}},
        {'id': 9, 'name': {'ja': 'PH タイプ09', 'zh': 'PH 類型09'}},
        {'id': 9, 'name': {'ja': 'PH タイプ10', 'zh': 'PH 類型09'}},
        {'id': 9, 'name': {'ja': 'PH タイプ11', 'zh': 'PH 類型09'}},
        {'id': 9, 'name': {'ja': 'PH タイプ12', 'zh': 'PH 類型09'}},
        {'id': 9, 'name': {'ja': 'HS Aタイプ01', 'zh': 'HS A類型01'}},
        {'id': 9, 'name': {'ja': 'HS Aタイプ02', 'zh': 'HS A類型02'}},
        {'id': 9, 'name': {'ja': 'HS Aタイプ03', 'zh': 'HS A類型03'}},
        {'id': 9, 'name': {'ja': 'HS Aタイプ04', 'zh': 'HS A類型04'}},
        {'id': 9, 'name': {'ja': 'HS Aタイプ05', 'zh': 'HS A類型05'}},
        {'id': 9, 'name': {'ja': 'HS Aタイプ06', 'zh': 'HS A類型06'}},
        {'id': 9, 'name': {'ja': 'HS Aタイプ07', 'zh': 'HS A類型07'}},
        {'id': 9, 'name': {'ja': 'HS Aタイプ08', 'zh': 'HS A類型08'}},
        {'id': 9, 'name': {'ja': 'HS Aタイプ09', 'zh': 'HS A類型09'}},
        {'id':  9, 'name': {'ja': 'HS Aタイプ10', 'zh': 'HS A類型10'}},
        {'id': 10, 'name': {'ja': 'HS Aタイプ11', 'zh': 'HS A類型11'}},
        {'id': 9, 'name': {'ja': 'HS Aタイプ12', 'zh': 'HS A類型12'}},
        {'id': 9, 'name': {'ja': 'HS Aタイプ13', 'zh': 'HS A類型13'}},
        {'id': 9, 'name': {'ja': 'HS Aタイプ14', 'zh': 'HS A類型14'}},
        {'id': 9, 'name': {'ja': 'HS Aタイプ15', 'zh': 'HS A類型15'}},
        {'id': 9, 'name': {'ja': 'HS Aタイプ16', 'zh': 'HS A類型16'}},
        {'id': 9, 'name': {'ja': 'HS Aタイプ17', 'zh': 'HS A類型17'}},
        {'id': 9, 'name': {'ja': 'HS Aタイプ18', 'zh': 'HS A類型18'}},
        {'id': 9, 'name': {'ja': 'HS Aタイプ19', 'zh': 'HS A類型19'}},
        {'id': 9, 'name': {'ja': 'HS Aタイプ20', 'zh': 'HS A類型20'}},
        {'id': 9, 'name': {'ja': 'HS Aタイプ21', 'zh': 'HS A類型21'}},
        {'id': 9, 'name': {'ja': 'HS Aタイプ22', 'zh': 'HS A類型22'}},
        {'id': 9, 'name': {'ja': 'HS Bタイプ01', 'zh': 'HS B類型01'}},
        {'id': 9, 'name': {'ja': 'HS Bタイプ02', 'zh': 'HS B類型02'}},
        {'id': 9, 'name': {'ja': 'HS Bタイプ03', 'zh': 'HS B類型03'}},
        {'id': 9, 'name': {'ja': 'HS Bタイプ04', 'zh': 'HS B類型04'}},
        {'id': 9, 'name': {'ja': 'HS Bタイプ05', 'zh': 'HS B類型05'}},
        {'id': 9, 'name': {'ja': 'HS Bタイプ06', 'zh': 'HS B類型06'}},
        {'id': 9, 'name': {'ja': 'HS Bタイプ07', 'zh': 'HS B類型07'}},
    ],
    'chest_textures': [
        {'id': (0, 0), 'type': '紋理', 'name': {'ja': 'なし', 'zh': '無'}},
        {'id': (1, 0), 'type': '紋理', 'name': {'ja': 'タトゥー(龍)', 'zh': '紋身(龍)'}},
        {'id': (2, 0), 'type': '紋理', 'name': {'ja': '筋肉線', 'zh': '肌肉線條'}},
        # ... 其他胸部紋理
    ]
}

def get_localized_name(name_dict, lang):
    '''日文優先（預設為 ja），找不到才退回中文（zh）'''
    return name_dict.get(lang) or name_dict.get('ja') or name_dict.get('zh') or '???'
    
def get_face_by_id(category: str, face_id: int, lang: str = 'ja') -> str:
    for item in FACE_DETAILS.get(category, []):
        if item['id'] == face_id:
            return get_localized_name(item['name'], lang)
    
    # 根據語言返回找不到的提示
    not_found_messages = {
        'ja': f'顔設定ID {face_id} が見つかりません',
        'zh': f'找不到臉部設定 ID {face_id}',
    }
    return not_found_messages.get(lang, f'Face ID {face_id} not found')
    
# 輔助函數 (與 accessory_data.py 中的類似)
def get_body_detail_name_by_id(category: str, item_id_tuple: tuple[int, int], lang: str = 'ja') -> str:
    # 實現查找邏輯
    pass

def get_body_detail_type(category: str, item_id_tuple: tuple[int, int]) -> str:
    # 實現查找類型邏輯
    pass            