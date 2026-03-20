# ph-editor/game_data/life_stage.py
import re
from typing import Optional, List, Dict, Any

# 1. 核心數據定義 (使用 int 作為 ID)
LIFE_STAGES_DATA = {
    1: {"short": "懷春", "name": "少女前期", "age": "15-17", "desc": "少女幻想戀愛的可能"},
    2: {"short": "戀夏", "name": "少女中期", "age": "18-19", "desc": "少女的暗戀"},
    3: {"short": "悲秋", "name": "半步青春", "age": "20", "desc": "少女的失戀，但美少女青春無敵，沒有後期。"},
    4: {"short": "青澀", "name": "青澀期", "age": "21-22", "desc": "年輕女性一開始像青澀的果實"},
    5: {"short": "飽滿", "name": "飽滿期", "age": "23-24", "desc": "年輕女性像果實一樣發育飽滿，例如胸部"},
    6: {"short": "熟成", "name": "熟成期", "age": "25-26", "desc": "年輕女性發育漸漸成熟"},
    7: {"short": "微醺", "name": "半步輕熟", "age": "27-28", "desc": "年輕女性"},
    8: {"short": "精緻", "name": "輕熟中", "age": "29-31", "desc": "輕熟女失去青春，追求精緻來彌。沒有前期，不存在微微熟的狀態"},
    9: {"short": "輕奢", "name": "輕熟後", "age": "32-34", "desc": "輕熟女精緻補不了，追求輕奢"},
    10: {"short": "敗犬", "name": "半步熟女", "age": "35", "desc": "輕熟女彌補青春失敗，成為敗犬"},
    11: {"short": "魚尾", "name": "熟女初期", "age": "36-37", "desc": "熟女固化魚尾紋了。"},
    12: {"short": "法令", "name": "熟女中期", "age": "38-40", "desc": "熟女固化法令紋了。"},
    13: {"short": "初老", "name": "初老期", "age": "41", "desc": "熟女的臉初顯老態"},
    14: {"short": "華髮", "name": "熟女末期", "age": "42-45", "desc": "熟女的末日，年齡容貌的焦慮到達頂點，這個時期還特別長。"},
    15: {"short": "醫美", "name": "半步美魔女", "age": "46-49", "desc": "熟女花了漫長的時間及金錢，希望能夠突破境界"},
    16: {"short": "不老", "name": "美魔女", "age": "50-", "desc": "美魔女逆齡凍顏不老。再老沒人看了。"},
}

# 4. 分組定義 (使用 ID 清單)
LIFE_STAGE_GROUPS = [
    {"group_name": "少女", "items": [1, 2, 3]},
    {"group_name": "年輕女性", "items": [4, 5, 6, 7]},
    {"group_name": "輕熟女", "items": [8, 9, 10]},
    {"group_name": "熟女", "items": [11, 12, 13, 14, 15]},
    {"group_name": "美魔女", "items": [16]}
]

# 1. 由 id 查出 lifeStage 資料
def get_lifestage_by_id(ls_id: int) -> Optional[Dict[str, Any]]:
    return LIFE_STAGES_DATA.get(ls_id)

# 5. 由 id 反查最小年齡 (處理 "a-b" 或 "b-")
def get_min_age(ls_id: int) -> Optional[int]:
    stage = LIFE_STAGES_DATA.get(ls_id)
    if not stage:
        return None
    
    # 使用正則表達式尋找第一個出現的數字數字
    # 例如 "0-2" 抓到 0, "76-" 抓到 76
    match = re.search(r"(\d+)", stage["age"])
    return int(match.group(1)) if match else None

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