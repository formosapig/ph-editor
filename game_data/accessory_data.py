# your_character_project/game_data/accessory_data.py

# colorful 說明同 clothing_data.py:
# 0 不能改顏色, 也不讀顏色資料
# 1 只能改主色, 副色強制 (255,255,255,255) (255,255,255,255) 0, 0
# 2 副色只能改光澤質感 (?, ?, ?, ?) (?, ?, ?, ?) Fix, ??
# 3 主副色都能隨意調整

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
    {'id': ( -1,  -1), 'colorful': 0, 'name': {'ja': 'なし', 'zh': '無'}},
    
    # 頭
    {'id': (  0, 500), 'colorful': 3, 'name': {'ja': 'CAキャップ(色)', 'zh': 'CA帽子(色)'}},
    {'id': (1, 2), 'colorful': 3, 'name': {'ja': '髪留め(色)', 'zh': '髮夾(色)'}},
    {'id': (1, 3), 'colorful': 3, 'name': {'ja': 'ヘアピン(色)', 'zh': '髮夾(色)'}},
    {'id': (1, 4), 'colorful': 3, 'name': {'ja': 'リボン(色)', 'zh': '絲帶(色)'}},
    {'id': (1, 5), 'colorful': 3, 'name': {'ja': 'カチューシャ(色)', 'zh': '髮箍(色)'}},
    {'id': (1, 6), 'colorful': 3, 'name': {'ja': 'アホ毛(色)', 'zh': '呆毛(色)'}},
    {'id': (1, 7), 'colorful': 3, 'name': {'ja': '觸覚毛(色)', 'zh': '觸角髮(色)'}},
    {'id': (1, 8), 'colorful': 3, 'name': {'ja': '付け三つ編み(色)', 'zh': '假三股辮(色)'}},
    {'id': (1, 9), 'colorful': 0, 'name': {'ja': 'ヘッドホン(黒)', 'zh': '耳機(黑)'}},
    
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

def is_colorful(item_id_tuple: tuple[int, int]) -> int:
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
        if item['id'] == item_id_tuple:
            return item.get('colorful', 0) # 預設為 0
    return 0 # 如果找不到對應的物品，返回 0