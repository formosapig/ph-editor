# ph-editor/game_data/cup_data.py

'''
                            上胸圍 - 下胸圍
                 3- 6  6- 9  9-12 12-15 15-18 18-21 21-24 24-27     衣服尺寸
下胸圍 67-72 cm   32AA  32A   32B   32C   32D                          XSS
      73-77 cm   34AA  34A   34B   34C   34D   34E                    XS 
      78-82 cm         36A   36B   36C   36D   36E   36F              S 
      83-87 cm         38A   38B   38C   38D   38E   38F   38G        M  
      88-92 cm                     40C   40D   40E   40F   40G        L 
      
      
罩杯等級, 32(XXS), 34(XS), 36(S), 38(M), 40(L)
AA,      0,        5,     10,     22,     35
A,       5,       10,     22,     35,     45
B,      10,       22,     35,     45,     50
C,22,35,45,50,52
D,35,45,50,52,54
E,45,50,52,54,55
F,50,52,55,57,58
G,52,55,58,59,60
H,55,58,60,62,65

下胸圍  罩杯	AA	A	B	C	D	E	F	G	H	I
30           6  12  20  29  36    
32 (70)	    10	18	25	35	42 (48	52	55	58	60)
34 (75)	   (15) 22	32	42	50	53 (56	59	62	64)
36 (80)	   (22	28)	38	48	55	58	61 (64	67	69)
38 (85)	   (28	35	45) 53	60	63	66	69 (72	74)
40 (90)	   (35	42	50	58)	65	71	74	77	80	82


衣服尺寸建議下胸圍 (基準)說明
XS / XSS 30 ~ 32 極其纖細的少女骨架
S        32 ~ 34 台灣女生最常見的骨架
M        34 ~ 36 稍微有肉或骨架正常的成熟女性
L        36 ~ 38 骨架寬大或整體豐滿的女性
XL       40+     大尺碼設定
'''

import re
from typing import Optional, List, Dict, Any

# 核心數據對照表 (已優化姊妹杯斜線)
SISTER_SIZE_CHART = {
    "30": [ 6, 10, 15, 20, 25],
    "32": [10, 15, 20, 26, 31, 41, 47, 52, 57, 62],
    "34": [15, 21, 27, 33, 39, 44, 50, 56, 62, 67],
    "36": [21, 27, 33, 39, 45, 50, 56, 62, 67, 72],
    "38": [27, 33, 39, 45, 51, 56, 61, 67, 72, 75],
    "40": [33, 39, 45, 51, 57, 62, 67, 72, 75, 78]
}

CUP_VALUE_MAP = {"AA": 0, "A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8, "I": 9}

CUP_GROUP_DEFINITIONS = [
    {"group_name": "纖細少女", "items": ["30AA", "30A", "30B"]},
    {"group_name": "身材嬌小", "items": ["32AA", "32A", "32B", "32C", "32D"]},
    {"group_name": "台灣女生", "items": ["34A", "34B", "34C", "34D", "34E", "34F"]},
    {"group_name": "骨架正常", "items": ["36B", "36C", "36D", "36E", "36F"]},
    {"group_name": "體態豐滿", "items": ["38C", "38D", "38E", "38F", "38G"]},
    {"group_name": "大尺碼", "items": ["40D", "40E", "40F", "40G", "40H", "40I"]}
]

def get_sister_cup_value(size_str: str) -> Optional[int]:
    """
    根據姊妹杯優化曲線回傳數值
    """
    match = re.match(r"(\d+)([A-I]+)", size_str.upper())
    if not match: return None
    
    underbust, cup = match.groups()
    if underbust in SISTER_SIZE_CHART and cup in CUP_VALUE_MAP:
        idx = CUP_VALUE_MAP[cup]
        data = SISTER_SIZE_CHART[underbust]
        return data[idx] if idx < len(data) else None
    return None

# 維持原有的 generate_cup_options 邏輯
def generate_cup_options() -> List[Dict[str, Any]]:
    options = []
    for group in CUP_GROUP_DEFINITIONS:
        options.append({"label": f"📏 {group['group_name']}", "value": "", "disabled": True})
        for size in group['items']:
            val = get_sister_cup_value(size)
            options.append({
                "label": size, #f"{size} ({val})",
                "value": size
            })
    return options