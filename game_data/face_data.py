# your_character_project/game_data/face_data.py

FACE_DETAILS = {
    # 輪廓
    'contour': [
        {'id': 0, 'name': {'ja': 'ヘッドA01', 'zh': '頭A01'}},
        {'id': 2, 'name': {'ja': 'ヘッドA02', 'zh': '頭A02'}},
        {'id': 3, 'name': {'ja': 'ヘッドA03', 'zh': '頭A03'}},
        {'id': 1, 'name': {'ja': 'ヘッドB', 'zh': '頭B'}},
    ],
    # 肌肉, 沒有全部檢查過. 只用插入法抽查幾個
    'muscle': [
        {'id': 500, 'name': {'ja': 'PH タイプ01', 'zh': 'PH 類型01'}},
        {'id': 501, 'name': {'ja': 'PH タイプ02', 'zh': 'PH 類型02'}},
        {'id': 502, 'name': {'ja': 'PH タイプ03', 'zh': 'PH 類型03'}},
        {'id': 503, 'name': {'ja': 'PH タイプ04', 'zh': 'PH 類型04'}},
        {'id': 504, 'name': {'ja': 'PH タイプ05', 'zh': 'PH 類型05'}},
        {'id': 505, 'name': {'ja': 'PH タイプ06', 'zh': 'PH 類型06'}},
        {'id': 506, 'name': {'ja': 'PH タイプ07', 'zh': 'PH 類型07'}},
        {'id': 507, 'name': {'ja': 'PH タイプ08', 'zh': 'PH 類型08'}},
        {'id': 508, 'name': {'ja': 'PH タイプ09', 'zh': 'PH 類型09'}},
        {'id': 509, 'name': {'ja': 'PH タイプ10', 'zh': 'PH 類型09'}},
        {'id': 510, 'name': {'ja': 'PH タイプ11', 'zh': 'PH 類型09'}},
        {'id': 511, 'name': {'ja': 'PH タイプ12', 'zh': 'PH 類型09'}},
        {'id':   0, 'name': {'ja': 'HS Aタイプ01', 'zh': 'HS A類型01'}},
        {'id':   1, 'name': {'ja': 'HS Aタイプ02', 'zh': 'HS A類型02'}},
        {'id':   2, 'name': {'ja': 'HS Aタイプ03', 'zh': 'HS A類型03'}},
        {'id':   3, 'name': {'ja': 'HS Aタイプ04', 'zh': 'HS A類型04'}},
        {'id':   4, 'name': {'ja': 'HS Aタイプ05', 'zh': 'HS A類型05'}},
        {'id':   5, 'name': {'ja': 'HS Aタイプ06', 'zh': 'HS A類型06'}},
        {'id':   6, 'name': {'ja': 'HS Aタイプ07', 'zh': 'HS A類型07'}},
        {'id':   7, 'name': {'ja': 'HS Aタイプ08', 'zh': 'HS A類型08'}},
        {'id':   8, 'name': {'ja': 'HS Aタイプ09', 'zh': 'HS A類型09'}},
        {'id':   9, 'name': {'ja': 'HS Aタイプ10', 'zh': 'HS A類型10'}},
        {'id':  10, 'name': {'ja': 'HS Aタイプ11', 'zh': 'HS A類型11'}},
        {'id':  11, 'name': {'ja': 'HS Aタイプ12', 'zh': 'HS A類型12'}},
        {'id':  12, 'name': {'ja': 'HS Aタイプ13', 'zh': 'HS A類型13'}},
        {'id':  13, 'name': {'ja': 'HS Aタイプ14', 'zh': 'HS A類型14'}},
        {'id':  14, 'name': {'ja': 'HS Aタイプ15', 'zh': 'HS A類型15'}},
        {'id':  15, 'name': {'ja': 'HS Aタイプ16', 'zh': 'HS A類型16'}},
        {'id':  16, 'name': {'ja': 'HS Aタイプ17', 'zh': 'HS A類型17'}},
        {'id':  17, 'name': {'ja': 'HS Aタイプ18', 'zh': 'HS A類型18'}},
        {'id':  18, 'name': {'ja': 'HS Aタイプ19', 'zh': 'HS A類型19'}},
        {'id':  26, 'name': {'ja': 'HS Aタイプ20', 'zh': 'HS A類型20'}},
        {'id':  27, 'name': {'ja': 'HS Aタイプ21', 'zh': 'HS A類型21'}},
        {'id':  28, 'name': {'ja': 'HS Aタイプ22', 'zh': 'HS A類型22'}},
        {'id':  19, 'name': {'ja': 'HS Bタイプ01', 'zh': 'HS B類型01'}},
        {'id':  20, 'name': {'ja': 'HS Bタイプ02', 'zh': 'HS B類型02'}},
        {'id':  21, 'name': {'ja': 'HS Bタイプ03', 'zh': 'HS B類型03'}},
        {'id':  22, 'name': {'ja': 'HS Bタイプ04', 'zh': 'HS B類型04'}},
        {'id':  23, 'name': {'ja': 'HS Bタイプ05', 'zh': 'HS B類型05'}},
        {'id':  24, 'name': {'ja': 'HS Bタイプ06', 'zh': 'HS B類型06'}},
        {'id':  25, 'name': {'ja': 'HS Bタイプ07', 'zh': 'HS B類型07'}},
    ],
    # 皺紋
    'wrinkle': [
        {'id':   0, 'name': {'ja': 'なし', 'zh': '無'}},
        {'id':   1, 'name': {'ja': '彫りの深さ1', 'zh': '雕刻深度1'}},
        {'id':   5, 'name': {'ja': '彫りの深さ2', 'zh': '雕刻深度2'}},
        {'id':   2, 'name': {'ja': '口元1', 'zh': '嘴巴1'}},
        {'id':   3, 'name': {'ja': '目元1', 'zh': '眼睛1'}},
        {'id':   4, 'name': {'ja': '目元2', 'zh': '眼睛2'}},
        {'id':   6, 'name': {'ja': '目元3', 'zh': '眼睛3'}},
        {'id':   7, 'name': {'ja': '目元4', 'zh': '眼睛4'}},
        {'id':   8, 'name': {'ja': '全体詳細', 'zh': '整體細節'}},
        {'id':   9, 'name': {'ja': 'メカモールド1', 'zh': '機械模具1'}},
        {'id':  10, 'name': {'ja': 'メカモールド2', 'zh': '機械模具2'}},
    ],
    # 眉毛形狀
    'eyebrows' : [
        {'id': ( 500, 2), 'name': {'ja': '細め(長)02', 'zh': '細長02'}},
        {'id': ( 501, 2), 'name': {'ja': 'ナチュラルC', 'zh': '自然C'}},
        {'id': ( 502, 2), 'name': {'ja': 'ナチュラルD', 'zh': '自然D'}},
        {'id': (   0, 2), 'name': {'ja': '普通(長)', 'zh': '普通(長)'}},
        {'id': (   1, 2), 'name': {'ja': '普通(中)', 'zh': '普通(中)'}},
        {'id': (   2, 2), 'name': {'ja': '普通(短)', 'zh': '普通(短)'}},
        {'id': None, 'name': {'ja': '細め(長)', 'zh': '細長'}},
        {'id': None, 'name': {'ja': '細め(中)', 'zh': '細中'}},
        {'id': None, 'name': {'ja': '細め(短)', 'zh': '細短'}},
        {'id': None, 'name': {'ja': '太め(長)', 'zh': '粗長'}},
        {'id': None, 'name': {'ja': '太め(中)', 'zh': '粗中'}},
        {'id': None, 'name': {'ja': '太め(短)', 'zh': '粗短'}},
        {'id': None, 'name': {'ja': 'への字', 'zh': '八字形'}},
        {'id': None, 'name': {'ja': 'アーチ', 'zh': '拱形'}},
        {'id': None, 'name': {'ja': '尻上がり', 'zh': '上揚'}},
        {'id': None, 'name': {'ja': '尻すぼみ', 'zh': '下垂'}},
        {'id': (  13, 2), 'name': {'ja': '末広がり', 'zh': '末端寬廣'}},
        {'id': (0, 0), 'name': {'ja': '細い', 'zh': '細'}},
        {'id': (0, 0), 'name': {'ja': 'まる', 'zh': '圓形'}},
        {'id': (0, 0), 'name': {'ja': 'ちょび', 'zh': '小'}},
        {'id': (0, 0), 'name': {'ja': 'フェード', 'zh': '淡出'}},
        {'id': (0, 0), 'name': {'ja': 'かまぼこ', 'zh': '魚板形'}},
        {'id': (  19, 2), 'name': {'ja': 'ごんぶと', 'zh': '粗'}},
        {'id': (  20, 2), 'name': {'ja': 'ファニー', 'zh': '滑稽'}},
        {'id': (  21, 2), 'name': {'ja': 'ストロング', 'zh': '強烈'}},
        {'id': (0, 0), 'name': {'ja': '太めのカーブ', 'zh': '粗曲線'}},
        {'id': (0, 0), 'name': {'ja': '普通フェード', 'zh': '普通淡出'}},
        {'id': (0, 0), 'name': {'ja': 'ナチュラルA', 'zh': '自然A'}},
        {'id': (0, 0), 'name': {'ja': 'ナチュラルB', 'zh': '自然B'}},
        {'id': (  24, 2), 'name': {'ja': 'ショートカーブ', 'zh': '短曲線'}},
        {'id': (0, 0), 'name': {'ja': 'ゆるやかカーブ', 'zh': '緩曲線'}},
        {'id': (0, 0), 'name': {'ja': '細カーブ', 'zh': '細曲線'}},
        {'id': (0, 0), 'name': {'ja': '薄眉', 'zh': '薄眉'}},
        {'id': (  30, 2), 'name': {'ja': '薄細', 'zh': '薄細'}},
    ],
}

def get_localized_name(name_dict, lang):
    '''日文優先（預設為 ja），找不到才退回中文（zh）'''
    return name_dict.get(lang) or name_dict.get('ja') or name_dict.get('zh') or '???'
    
def get_face_by_id(category: str, face_id: int | tuple[int, int], lang: str = 'ja') -> str:
    candidates = FACE_DETAILS.get(category, [])

    # 單一 ID：int
    if isinstance(face_id, int):
        for item in candidates:
            if item.get('id') == face_id:
                return get_localized_name(item['name'], lang)
        id_repr = str(face_id)

    # 雙 ID：tuple[int, int]
    elif (
        isinstance(face_id, tuple)
        and len(face_id) == 2
        and all(isinstance(i, int) for i in face_id)
    ):
        for item in candidates:
            if item.get('id') == face_id:
                return get_localized_name(item['name'], lang)
        id_repr = f'({face_id[0]}, {face_id[1]})'

    else:
        raise TypeError(f'Invalid face_id type: {face_id!r}')

    # 找不到時的訊息
    not_found_messages = {
        'ja': f'顔設定ID {id_repr} が見つかりません',
        'zh': f'找不到臉部設定 ID {id_repr}',
    }
    return not_found_messages.get(lang, f'Face ID {id_repr} not found')
    
# 輔助函數 (與 accessory_data.py 中的類似)
def get_body_detail_name_by_id(category: str, item_id_tuple: tuple[int, int], lang: str = 'ja') -> str:
    # 實現查找邏輯
    pass

def get_body_detail_type(category: str, item_id_tuple: tuple[int, int]) -> str:
    # 實現查找類型邏輯
    pass            