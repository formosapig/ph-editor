# hair_data.py

HAIR_STYLES = {
    'back': [
        # set 髮
        {'id': (502, 1), 'set' : True, 'accessory': True, 'name': {'ja': '雪子ローポニー(左)', 'zh': '雪子低馬尾（左）'}},
        {'id': (503, 1), 'set' : True, 'accessory': True, 'name': {'ja': 'ローポニー(右)', 'zh': '低馬尾（右）'}},
        {'id': (506, 1), 'set' : True,                    'name': {'ja': '真理子ショート', 'zh': '真理子短髮'}},
        {'id': (  5, 1), 'set' : True,                    'name': {'ja': 'フェミニンボブ', 'zh': '女性化波波頭'}},
        {'id': (  8, 1), 'set' : True,                    'name': {'ja': 'ショートボブ', 'zh': '短波波頭'}},
        {'id': ( 18, 1), 'set' : True,                    'name': {'ja': 'サイドアップ(キャップ)', 'zh': '側邊紮髮（棒球帽）'}},
        {'id': ( 25, 1), 'set' : True,                    'name': {'ja': 'ボウズ', 'zh': '光頭'}},
        {'id': ( 26, 1), 'set' : True,                    'name': {'ja': 'ミディアムウェーブ', 'zh': '中長波浪髮'}},
        {'id': ( 27, 1), 'set' : True,                    'name': {'ja': 'べリーショート', 'zh': '超短髮'}},
        {'id': ( 39, 1), 'set' : True,                    'name': {'ja': 'くせっ毛ロング', 'zh': '自然捲長髮'}},
        {'id': ( 44, 1), 'set' : True,                    'name': {'ja': 'シトリーの髮型', 'zh': 'シトリー的髮型'}},
        {'id': ( 48, 1), 'set' : True,                    'name': {'ja': 'ホイップカール', 'zh': '蓬鬆捲髮'}},
        {'id': ( 50, 1), 'set' : True, 'accessory': True, 'name': {'ja': 'シスターべール', 'zh': '修女頭紗髮型'}},
        {'id': ( 51, 1), 'set' : True, 'accessory': True, 'name': {'ja': 'アレンジおさげ', 'zh': '造型雙辮子'}},
        # back 髮
        {'id': (500, 1),                    'name': {'ja': '律子ロング', 'zh': '律子長髮'}},
        {'id': (501, 1),                    'name': {'ja': '明子ミディアム', 'zh': '明子中長髮'}},
        {'id': (504, 1),                    'name': {'ja': 'ボブ', 'zh': '波波頭'}},
        {'id': (505, 1),                    'name': {'ja': 'ショート', 'zh': '短髮'}},
        {'id': (  0, 1),                    'name': {'ja': '外ハネショート', 'zh': '外翹短髮'}},
        {'id': (  1, 1),                    'name': {'ja': 'ゆるふわロング', 'zh': '空氣感長髮'}},
        {'id': (  4, 1),                    'name': {'ja': 'カジュアルショート', 'zh': '休閒短髮'}},
        {'id': (  6, 1), 'accessory': True, 'name': {'ja': 'ウエーブロング', 'zh': '捲長髮'}},
        {'id': (  7, 1),                    'name': {'ja': 'ロングストレート', 'zh': '直長髮'}},
        {'id': (  9, 1), 'accessory': True, 'name': {'ja': 'ツインロール', 'zh': '雙捲髮'}},
        {'id': ( 10, 1),                    'name': {'ja': '外ハネロング', 'zh': '外翹長髮'}},
        {'id': ( 11, 1),                    'name': {'ja': 'お団子アレンジ', 'zh': '日式糰子頭'}},
        {'id': ( 12, 1),                    'name': {'ja': 'シャギーセミショート', 'zh': '層次中短髮'}},
        {'id': ( 23, 1), 'accessory': True, 'name': {'ja': 'ショートツイン', 'zh': '短髮雙馬尾'}}, # 分格是 02 00 00 00 
        {'id': ( 13, 1), 'accessory': True, 'name': {'ja': 'ショートツインアクセ', 'zh': '短髮雙馬尾(配飾)'}},
        {'id': ( 14, 1),                    'name': {'ja': 'ゆるふわレイヤー', 'zh': '柔軟蓬鬆分層'}},
        {'id': ( 15, 1), 'accessory': True, 'name': {'ja': 'チャイナポンポン', 'zh': '中式雙髮髻'}},
        {'id': ( 16, 1), 'accessory': True, 'name': {'ja': 'ロングツインテール', 'zh': '長髮雙馬尾'}},
        {'id': ( 17, 1), 'accessory': True, 'name': {'ja': 'ツインシュリンプロール', 'zh': '雙馬尾縮捲髮'}},
        {'id': ( 19, 1), 'accessory': True, 'name': {'ja': 'サイドアップ', 'zh': '側邊盤髮'}},
        {'id': (  2, 1),                    'name': {'ja': 'ロングポニー', 'zh': '長馬尾'}},
        {'id': (  3, 1), 'accessory': True, 'name': {'ja': 'ロングポニー(頭巾)', 'zh': '長馬尾（頭巾）'}},
        {'id': ( 20, 1), 'accessory': True, 'name': {'ja': 'リボンポニーロング', 'zh': '緞帶長馬尾'}},
        {'id': ( 21, 1),                    'name': {'ja': 'シャギーロング', 'zh': '層次長髮'}},
        {'id': ( 22, 1), 'accessory': True, 'name': {'ja': 'リボンポニーショート', 'zh': '緞帶短馬尾'}},
        {'id': ( 24, 1), 'accessory': True, 'name': {'ja': '三つ編みツイン', 'zh': '雙三股辮'}},
        {'id': ( 28, 1),                    'name': {'ja': 'ガーリーボブ(後ろ)', 'zh': '甜美波波頭（後髮）'}},
        {'id': ( 29, 1),                    'name': {'ja': 'チャイナシ二ヨン(後ろ)', 'zh': '中國髮髻（後髮）'}},
        {'id': ( 32, 1), 'accessory': True, 'name': {'ja': 'ハロウィンヘアー(後ろ)', 'zh': '萬聖髮型（後髮）'}},
        {'id': ( 33, 1), 'accessory': True, 'name': {'ja': '三つ編みロング(後ろ)', 'zh': '長三股辮（後髮）'}},
        {'id': ( 34, 1), 'accessory': True, 'name': {'ja': 'カールロングポニー', 'zh': '捲髮長馬尾'}},
        {'id': ( 35, 1), 'accessory': True, 'name': {'ja': 'カールロングポニーリボン', 'zh': '緞帶捲髮長馬尾'}},
        {'id': ( 36, 1), 'accessory': True, 'name': {'ja': 'おさげ', 'zh': '雙辮子'}},
        {'id': ( 37, 1), 'accessory': True, 'name': {'ja': 'おさげリボン', 'zh': '緞帶雙辮子'}},
        {'id': ( 38, 1),                    'name': {'ja': 'ミディアムマッシュ', 'zh': '中長蘑菇頭'}},
        {'id': ( 40, 1),                    'name': {'ja': '外ハネシャギー(後ろ)', 'zh': '外翹蓬鬆髮（後面）'}},
        {'id': ( 41, 1),                    'name': {'ja': 'バエル後ろ髪', 'zh': '吸睛後髮'}},
        {'id': ( 42, 1),                    'name': {'ja': 'グラデーションボブ(後ろ)', 'zh': '漸層波波頭（後髮）'}},
        {'id': ( 43, 1),                    'name': {'ja': 'うどん毛ロング(後ろ)', 'zh': '自然捲長髮（後髮）'}},
        {'id': ( 45, 1),                    'name': {'ja': 'アップポニー', 'zh': '高馬尾'}},
        {'id': ( 46, 1), 'accessory': True, 'name': {'ja': 'ベリーロングツインテール(後ろ)', 'zh': '超長雙馬尾（後髮）'}},
        {'id': ( 47, 1), 'accessory': True, 'name': {'ja': 'ツーサイドアップ(後ろ)', 'zh': '披肩雙馬尾（後髮）'}},
        {'id': ( 52, 1), 'accessory': True, 'name': {'ja': 'ベリーロングツインテール(太ろ)', 'zh': '超長雙馬尾（粗）'}},
        {'id': ( 53, 1), 'accessory': True, 'name': {'ja': 'ストレートポニー', 'zh': '直髮馬尾'}},
        {'id': ( 54, 1),                    'name': {'ja': 'ベリーロングストレート', 'zh': '超長直髮'}},
        {'id': ( 55, 1), 'accessory': True, 'name': {'ja': '三つ編みサイド', 'zh': '側三股辮'}},
        {'id': ( 56, 1), 'accessory': True, 'name': {'ja': 'ロングサイド', 'zh': '側長髮'}},
        {'id': ( 57, 1), 'accessory': True, 'name': {'ja': '三つ編みフード', 'zh': '帽下三股辮'}},
        {'id': ( 58, 1), 'accessory': True, 'name': {'ja': '紐結いシニヨン', 'zh': '束繩髮髻'}},
    ],
    'side': [ 
        {'id': (  0, 1),                    'name': {'ja': 'なし', 'zh': '無'}},
        {'id': (  1, 1),                    'name': {'ja': '細ロング', 'zh': '細長髮'}},
        {'id': (  2, 1),                    'name': {'ja': '太ロング', 'zh': '粗長髮'}},
        {'id': (  3, 1),                    'name': {'ja': 'ショート', 'zh': '短髮'}},
        {'id': (  4, 1),                    'name': {'ja': 'べリーショート', 'zh': '超短髮'}},
        {'id': (  5, 1),                    'name': {'ja': 'ストレート', 'zh': '直髮'}},
        {'id': (  6, 1),                    'name': {'ja': 'ロール', 'zh': '捲髮'}},
        {'id': (  7, 1), 'accessory': True, 'name': {'ja': '結びロング', 'zh': '長束髮'}}
    ],
    'front': [
        {'id': (  0, 1),                    'name': {'ja': 'なし', 'zh': '無'}},
        {'id': (500, 1),                    'name': {'ja': '律子ぱっつん', 'zh': '律子齊瀏海'}},
        {'id': (501, 1),                    'name': {'ja': 'ぱっつんサイドショート', 'zh': '齊瀏海側短髮'}},
        {'id': (502, 1),                    'name': {'ja': '明子64分け(左)', 'zh': '明子六四分線（左）'}},
        {'id': (503, 1),                    'name': {'ja': '64分け(右)', 'zh': '六四分線（右）'}},
        {'id': (504, 1),                    'name': {'ja': '64分けサイド內巻き', 'zh': '六四分線內捲側髮'}},
        {'id': (505, 1),                    'name': {'ja': 'シャギー', 'zh': '層次髮'}},
        {'id': (  1, 1),                    'name': {'ja': 'ぱっつんショート', 'zh': '齊瀏海短髮'}},
        {'id': (  2, 1),                    'name': {'ja': 'ぱっつんロング', 'zh': '齊瀏海長髮'}},
        {'id': (  3, 1),                    'name': {'ja': 'サイド分け', 'zh': '側分瀏海'}},
        {'id': (  5, 1),                    'name': {'ja': 'セミショート', 'zh': '中短髮'}},
        {'id': (  6, 1),                    'name': {'ja': 'ウエーブロング', 'zh': '捲長髮'}},
        {'id': (  7, 1), 'accessory': True, 'name': {'ja': 'リボンロング', 'zh': '緞帶長髮'}},
        {'id': (  8, 1),                    'name': {'ja': 'シャギーショート', 'zh': '層次短髮'}},
        {'id': (  9, 1),                    'name': {'ja': '內ハネセミショート', 'zh': '內彎中短髮'}},
        {'id': ( 10, 1),                    'name': {'ja': 'センター分けロング', 'zh': '中分長髮'}},
        {'id': ( 11, 1),                    'name': {'ja': 'シャギーセミショート', 'zh': '層次中短髮'}},
        {'id': ( 12, 1),                    'name': {'ja': 'クロスショート', 'zh': '交叉短髮'}},
        {'id': ( 13, 1),                    'name': {'ja': 'ゆるふわセミショート', 'zh': '蓬鬆中短髮'}},
        {'id': ( 14, 1),                    'name': {'ja': 'チャイナ分け', 'zh': '中式分線'}},
        {'id': ( 15, 1),                    'name': {'ja': 'ぱっつんシャギー', 'zh': '齊瀏海層次髮'}},
        {'id': ( 16, 1),                    'name': {'ja': 'センター分けショート', 'zh': '中分短髮'}},
        {'id': ( 17, 1),                    'name': {'ja': 'ライトロング', 'zh': '右側長髮'}},
        {'id': ( 19, 1),                    'name': {'ja': '內ハネロング', 'zh': '內彎長髮'}},
        {'id': ( 20, 1),                    'name': {'ja': 'レフトロング', 'zh': '左側長髮'}},
        {'id': ( 21, 1),                    'name': {'ja': 'センター分けシャギー', 'zh': '中分層次髮'}},
        {'id': ( 22, 1),                    'name': {'ja': 'ぱっつんストレート', 'zh': '齊瀏海直髮'}},
        {'id': ( 18, 1),                    'name': {'ja': 'ガーリーボブ(前)', 'zh': '甜美波波頭（前髮）'}},
        {'id': ( 23, 1), 'accessory': True, 'name': {'ja': 'チャイナシニヨン(前)', 'zh': '中國髮髻（前）'}},
        {'id': ( 24, 1),                    'name': {'ja': 'ハロウィンヘアー(前)', 'zh': '萬聖髮型（前）'}},
        {'id': ( 25, 1),                    'name': {'ja': '三つ編みロング(前)', 'zh': '長三股辮（前）'}},
        {'id': ( 26, 1),                    'name': {'ja': 'でこ出しロング', 'zh': '露額長髮'}},
        {'id': ( 27, 1),                    'name': {'ja': 'ミディアムシャギー', 'zh': '中長層次髮'}},
        {'id': ( 28, 1),                    'name': {'ja': 'ウインドショート(左)', 'zh': '風吹短髮（左）'}},
        {'id': ( 29, 1),                    'name': {'ja': 'ウインドショート(右)', 'zh': '風吹短髮（右）'}},
        {'id': ( 30, 1),                    'name': {'ja': '外ハネシャギー(前)', 'zh': '外翹層次髮（前）'}},
        {'id': ( 31, 1),                    'name': {'ja': 'バエル前髪', 'zh': '吸睛前髮'}},
        {'id': ( 32, 1),                    'name': {'ja': 'グラデーションボブ(前)', 'zh': '漸層波波頭（前）'}},
        {'id': ( 33, 1),                    'name': {'ja': 'うどん毛ロング(前)', 'zh': '自然捲長髮（前）'}},
        {'id': ( 34, 1),                    'name': {'ja': '內巻きセミショート', 'zh': '內捲中短髮'}},
        {'id': ( 35, 1),                    'name': {'ja': 'ベリーロングツインテール(前)', 'zh': '超長雙馬尾（前）'}},
        {'id': ( 36, 1),                    'name': {'ja': 'ツーサイドアップ(前)', 'zh': '雙側盤髮（前）'}},
        {'id': ( 37, 1),                    'name': {'ja': 'チャイナシニヨン(飾り無し)', 'zh': '中國髮髻（無飾）'}},
        {'id': ( 38, 1), 'accessory': True, 'name': {'ja': '橫結び', 'zh': '橫向束髮'}},
        {'id': ( 39, 1),                    'name': {'ja': 'サイド分けウエーブロング', 'zh': '側分捲長髮'}},
        {'id': ( 40, 1),                    'name': {'ja': 'アシメミディアム', 'zh': '不對稱中長髮'}},
        {'id': ( 41, 1),                    'name': {'ja': 'サイド分けミディアム', 'zh': '側分中長髮'}},
        {'id': ( 42, 1),                    'name': {'ja': 'ぱっつんベリーショート', 'zh': '齊瀏海極短髮'}}
    ]
}

def get_localized_name(name_dict, lang):
    '''日文優先（預設為 ja），找不到才退回中文（zh）'''
    return name_dict.get(lang) or name_dict.get('ja') or name_dict.get('zh') or '???'

def get_all_hair(lang: str = 'ja'):
    return {
        category: [
            {'id': item['id'], 'name': get_localized_name(item['name'], lang)}
            for item in items
        ]
        for category, items in HAIR_STYLES.items()
    }

def get_hair_by_category(category: str, lang: str = 'ja'):
    items = HAIR_STYLES.get(category, [])
    return [
        {'id': item['id'], 'name': get_localized_name(item['name'], lang)}
        for item in items
    ]

def get_hair_by_id(category: str, hair_id: tuple[int, int], lang: str = 'ja') -> str:
    for item in HAIR_STYLES.get(category, []):
        if item['id'] == hair_id:
            return get_localized_name(item['name'], lang)
    
    # 根據語言返回找不到的提示
    not_found_messages = {
        'ja': f'髪型ID {hair_id} が見つかりません',
        'zh': f'找不到髮型 ID {hair_id}',
    }
    return not_found_messages.get(lang, f'Hair ID {hair_id} not found')
    
def has_accessory(category: str, hair_id: tuple[int, int]) -> bool:
    for item in HAIR_STYLES.get(category, []):
        if item['id'] == hair_id:
            return item.get('accessory', False)
    return False
     
def is_set(category: str, hair_id: tuple[int, int]) -> bool:
    for item in HAIR_STYLES.get(category, []):
        if item['id'] == hair_id:
            return item.get('set', False)
    return False