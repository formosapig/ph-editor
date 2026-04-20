# ph-editor/game_data/life_stage.py
import re
from typing import Optional, List, Dict, Any

# 1. 核心數據定義 (使用 int 作為 ID)
LIFE_STAGES_DATA = {
    1: {"short": "懷春", "name": "少女前期", "age": 15, "desc": "少女幻想戀愛的可能"},
    2: {"short": "懷春", "name": "少女前期", "age": 16, "desc": "少女幻想戀愛的可能"},
    3: {"short": "懷春", "name": "少女前期", "age": 17, "desc": "少女幻想戀愛的可能"},
    4: {"short": "戀夏", "name": "少女中期", "age": 18, "desc": "少女的暗戀"},
    5: {"short": "戀夏", "name": "少女中期", "age": 19, "desc": "少女的暗戀"},
    6: {"short": "悲秋", "name": "半步青春", "age": 20, "desc": "少女的失戀，但美少女青春無敵，沒有後期。"},
    7: {"short": "青澀", "name": "青澀期", "age": 21, "desc": "年輕女性一開始像青澀的果實"},
    8: {"short": "青澀", "name": "青澀期", "age": 22, "desc": "年輕女性一開始像青澀的果實"},
    9: {"short": "飽滿", "name": "飽滿期", "age": 23, "desc": "年輕女性像果實一樣發育飽滿，例如胸部"},
    10: {"short": "飽滿", "name": "飽滿期", "age": 24, "desc": "年輕女性像果實一樣發育飽滿，例如胸部"},
    11: {"short": "熟成", "name": "熟成期", "age": 25, "desc": "年輕女性發育漸漸成熟"},
    12: {"short": "熟成", "name": "熟成期", "age": 26, "desc": "年輕女性發育漸漸成熟"},
    13: {"short": "微醺", "name": "半步輕熟", "age": 27, "desc": "年輕女性"},
    14: {"short": "微醺", "name": "半步輕熟", "age": 28, "desc": "年輕女性"},
    15: {"short": "精緻", "name": "輕熟中期", "age": 29, "desc": "輕熟女失去青春，追求精緻來彌。沒有前期，不存在微微熟的狀態"},
    16: {"short": "精緻", "name": "輕熟中期", "age": 30, "desc": "輕熟女失去青春，追求精緻來彌。沒有前期，不存在微微熟的狀態"},
    17: {"short": "精緻", "name": "輕熟中期", "age": 31, "desc": "輕熟女失去青春，追求精緻來彌。沒有前期，不存在微微熟的狀態"},
    18: {"short": "輕奢", "name": "輕熟後期", "age": 32, "desc": "輕熟女精緻補不了，追求輕奢"},
    19: {"short": "輕奢", "name": "輕熟後期", "age": 33, "desc": "輕熟女精緻補不了，追求輕奢"},
    20: {"short": "輕奢", "name": "輕熟後期", "age": 34, "desc": "輕熟女精緻補不了，追求輕奢"},
    21: {"short": "敗犬", "name": "半步熟女", "age": 35, "desc": "輕熟女彌補青春失敗，成為敗犬"},
    22: {"short": "魚尾", "name": "熟女初期", "age": 36, "desc": "熟女固化魚尾紋了。"},
    23: {"short": "魚尾", "name": "熟女初期", "age": 37, "desc": "熟女固化魚尾紋了。"},
    24: {"short": "法令", "name": "熟女中期", "age": 38, "desc": "熟女固化法令紋了。"},
    25: {"short": "法令", "name": "熟女中期", "age": 39, "desc": "熟女固化法令紋了。"},
    26: {"short": "法令", "name": "熟女中期", "age": 40, "desc": "熟女固化法令紋了。"},
    27: {"short": "初老", "name": "初老期", "age": 41, "desc": "熟女的臉初顯老態"},
    28: {"short": "華髮", "name": "熟女末期", "age": 42, "desc": "熟女的末日，年齡容貌的焦慮到達頂點，這個時期還特別長。"},
    29: {"short": "華髮", "name": "熟女末期", "age": 43, "desc": "熟女的末日，年齡容貌的焦慮到達頂點，這個時期還特別長。"},
    30: {"short": "華髮", "name": "熟女末期", "age": 44, "desc": "熟女的末日，年齡容貌的焦慮到達頂點，這個時期還特別長。"},
    31: {"short": "華髮", "name": "熟女末期", "age": 45, "desc": "熟女的末日，年齡容貌的焦慮到達頂點，這個時期還特別長。"},
    32: {"short": "醫美", "name": "半步美魔女", "age": 46, "desc": "熟女花了漫長的時間及金錢，希望能夠突破境界"},
    33: {"short": "醫美", "name": "半步美魔女", "age": 47, "desc": "熟女花了漫長的時間及金錢，希望能夠突破境界"},
    34: {"short": "醫美", "name": "半步美魔女", "age": 48, "desc": "熟女花了漫長的時間及金錢，希望能夠突破境界"},
    35: {"short": "醫美", "name": "半步美魔女", "age": 49, "desc": "熟女花了漫長的時間及金錢，希望能夠突破境界"},
    36: {"short": "不老", "name": "美魔女", "age": 50, "desc": "美魔女逆齡凍顏不老。再老沒人看了。"},
    37: {"short": "不老", "name": "美魔女", "age": 51, "desc": "美魔女逆齡凍顏不老。再老沒人看了。"},
    38: {"short": "不老", "name": "美魔女", "age": 52, "desc": "美魔女逆齡凍顏不老。再老沒人看了。"},
    39: {"short": "不老", "name": "美魔女", "age": 53, "desc": "美魔女逆齡凍顏不老。再老沒人看了。"},
    40: {"short": "不老", "name": "美魔女", "age": 54, "desc": "美魔女逆齡凍顏不老。再老沒人看了。"},
    41: {"short": "不老", "name": "美魔女", "age": 55, "desc": "美魔女逆齡凍顏不老。再老沒人看了。"},
}

# 4. 分組定義 (使用 ID 清單)
LIFE_STAGE_GROUPS = [
    {"group_name": "少女", "items": [1, 2, 3, 4, 5, 6]},
    {"group_name": "年輕女性", "items": [7, 8, 9, 10, 11, 12, 13, 14]},
    {"group_name": "輕熟女", "items": [15, 16, 17, 18, 19, 20, 21]},
    {"group_name": "熟女", "items": [22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35]},
    {"group_name": "美魔女", "items": [36, 37, 38, 39, 40, 41]}
]

# 1. 由 id 查出 lifeStage 資料
def get_lifestage_by_id(ls_id: int) -> Optional[Dict[str, Any]]:
    return LIFE_STAGES_DATA.get(ls_id)

# 5. 由 id 反查最小年齡 (處理 "a-b" 或 "b-")
def get_resonance_age(ls_id: int) -> Optional[int]:
    stage = LIFE_STAGES_DATA.get(ls_id)
    if not stage:
        return None
    return stage["age"]

# 6. 回傳 options 功能
def generate_lifestage_options() -> List[Dict[str, Any]]:
    #options = []
    options = [{
        "label": "-- 世界靜默 --",
        "pureLabel": "",  # 清除時 Label 設為空
        "value": ""       # 給前端判斷用的空字串
    }]
    for group in LIFE_STAGE_GROUPS:
        # 分組標題
        options.append({
            "label": group['group_name'],
            "value": None,
            "disabled": True
        })
        
        # 該組底下的項目
        for ls_id in group['items']:
            stage = LIFE_STAGES_DATA.get(ls_id)
            if stage:
                options.append({
                    "label": f"{stage['name']} ({stage['age']})",
                    "pureLabel": f"{stage['short']}",
                    "value": ls_id  # 這裡的 value 就是 int
                })
    return options