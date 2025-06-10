# your_character_project/game_data/accessory_data.py

# colorful 說明同 clothing_data.py:
# 0 不能改顏色, 也不讀顏色資料
# 1 只能改主色, 副色強制 (255,255,255,255) (255,255,255,255) 0, 0
# 2 副色只能改光澤質感 (?, ?, ?, ?) (?, ?, ?, ?) Fix, ??
# 3 主副色都能隨意調整

# ===== FLAG 定義區 =====
COLOR_MASK = 0b11        # 取 color 值
C0 = 0b00                # 無彩色
C1 = 0b01                # 僅主色可以
C2 = 0b10                # 主,副色可改, 但副色光澤強度鎖定
C3 = 0b11                # 主,副色可全部修改

# 配飾槽位的中文名稱陣列
ACCESSORY_SLOT_NAMES = [
    "頭",     # Accessory Slot 1
    "耳",     # Accessory Slot 2
    "眼鏡",   # Accessory Slot 3
    "臉",     # Accessory Slot 4
    "脖子",   # Accessory Slot 5
    "肩",     # Accessory Slot 6
    "乳房",   # Accessory Slot 7
    "腰",     # Accessory Slot 8
    "背後",   # Accessory Slot 9
    "腕",     # Accessory Slot 10 (通常可能還會有手、腳等，這裡根據您的10個槽位來列出)
    # 根據您的需求，如果還有更多配飾類別，可以在這裡繼續添加
    # 例如：
    # "手",
    # "腳",
]

ACCESSORY_ITEMS = [
    # 沒有
    
    {'id': ( -1,  -1), 'flag': C3,             'name': {'ja': 'なし', 'zh': '無'}},
        
    # 頭
    {'id': (  0, 500), 'flag': C2,             'name': {'ja': 'CAキャップ(色)', 'zh': 'CA帽(顏色)'}},
    {'id': (  0,  55), 'flag': C1,             'name': {'ja': '髪留め(色)', 'zh': '髮圈(顏色)'}},
    {'id': (  0,  56), 'flag': C1,             'name': {'ja': 'ヘアピン(色)', 'zh': '髮夾(顏色)'}},
    {'id': (  0,  50), 'flag': C1,             'name': {'ja': 'リボン(色)', 'zh': '髮帶(顏色)'}},
    {'id': (  0,  51), 'flag': C1,             'name': {'ja': 'カチューシャ(色)', 'zh': '髮箍(顏色)'}},
    {'id': (  0,  52), 'flag': C1,             'name': {'ja': 'アホ毛(色)', 'zh': '呆毛(顏色)'}},
    {'id': (  0,  53), 'flag': C1,             'name': {'ja': '触覚毛(色)', 'zh': '觸角髮(顏色)'}},
    {'id': (  0,  42), 'flag': C3,             'name': {'ja': '付け三つ編み(色)', 'zh': '附加三股辮(顏色)'}},
    {'id': (  0,   0),                         'name': {'ja': 'ヘッドホン(黒)', 'zh': '耳機(黑)'}},
    {'id': (  0,  22),                         'name': {'ja': 'ヘッドホン(白)', 'zh': '耳機(白)'}},
    {'id': (0, 0), 'flag': 'C0', 'name': {'ja': 'ヘッドホン(赤)', 'zh': '耳機(紅)'}},
    {'id': (0, 0), 'flag': 'C0', 'name': {'ja': '麦わら帽子(青)', 'zh': '草帽(藍)'}},
    {'id': (0, 0), 'flag': 'C0', 'name': {'ja': '麦わら帽子(赤)', 'zh': '草帽(紅)'}},
    {'id': (0, 0), 'flag': 'C0', 'name': {'ja': 'サンバイザーA(赤)', 'zh': '遮陽帽A(紅)'}},
    {'id': (0, 0), 'flag': 'C0', 'name': {'ja': 'サンバイザーA(白)', 'zh': '遮陽帽A(白)'}},
    {'id': (0, 0), 'flag': 'C0', 'name': {'ja': 'バニーカチューシャ(黒)', 'zh': '兔耳髮箍(黑)'}},
    {'id': (0, 0), 'flag': 'C0', 'name': {'ja': 'バニーカチューシャ(赤)', 'zh': '兔耳髮箍(紅)'}},
    {'id': (0, 0), 'flag': 'C0', 'name': {'ja': 'メイドカチューシャ', 'zh': '女僕髮箍'}},
    {'id': (0, 0), 'flag': 'C0', 'name': {'ja': 'ナース帽子(白)', 'zh': '護士帽(白)'}},


    
    {'id': (0, 0), 'colorful': 3, 'name': {'ja': 'なし', 'zh': '無'}}, # 預設無配飾
    {'id': (1, 0), 'colorful': 1, 'name': {'ja': 'メガネ', 'zh': '眼鏡'}},
    {'id': (2, 0), 'colorful': 3, 'name': {'ja': 'ヘッドホン', 'zh': '耳機'}},
    {'id': (3, 1), 'colorful': 0, 'name': {'ja': 'リボン(赤)', 'zh': '紅色蝴蝶結'}},
    {'id': (4, 1), 'colorful': 1, 'name': {'ja': 'カチューシャ(色)', 'zh': '髮箍(顏色)'}},
    # 更多配飾...
    {'id': (100, 5), 'colorful': 3, 'name': {'ja': '魔法の杖', 'zh': '魔法杖'}},
    {'id': (101, 0), 'colorful': 0, 'name': {'ja': '首輪', 'zh': '項圈'}},
]

def get_localized_name(name_dict: dict, lang: str = 'ja') -> str:
    '''日文優先（預設為 ja），找不到才退回中文（zh）'''
    return name_dict.get(lang) or name_dict.get('ja') or name_dict.get('zh') or '???'

def get_accessory_by_id(item_id_tuple: tuple[int, int], lang: str = 'ja') -> str:
    """
    根據 ID (種類ID, 特殊值) 獲取特定配飾物品的名稱。
    Args:
        item_id_tuple: 配飾物品的 ID 元組 (種類ID, 特殊值)。
        lang: 語言代碼 ('ja' 或 'zh')。
    Returns:
        配飾物品的本地化名稱。如果找不到則返回錯誤提示。
    """
    for item in ACCESSORY_ITEMS:
        if item['id'] == item_id_tuple:
            return get_localized_name(item['name'], lang)
            
    not_found_messages = {
        'ja': f'配飾ID {item_id_tuple} が見つかりません',
        'zh': f'找不到配飾 ID {item_id_tuple}',
    }
    return not_found_messages.get(lang, f'Accessory ID {item_id_tuple} not found')

def is_colorful(item_id: tuple[int, int]) -> int:
    """
    檢查指定配飾物品是否為可調顏色的。
    Args:
        item_id_tuple: 配飾物品的 ID 元組 (種類ID, 特殊值)。
    Returns:
        0 不能改顏色, 也不讀顏色資料
        1 只能改主色, 副色強制 (255,255,255,255) (255,255,255,255) 0, 0
        2 副色只能改光澤質感 (?, ?, ?, ?) (?, ?, ?, ?) Fix, ??
        3 主副色都能隨意調整
    """
    for item in ACCESSORY_ITEMS:
        if item['id'] == item_id:
            flag = item.get('flag', 0)
            return flag & COLOR_MASK
    return 0 # 如果找不到對應的物品，返回 0