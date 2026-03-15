# ph-editor/constants.py
from enum import IntEnum

# 特定檔案標頭（header）字串，用於辨識角色資料起始點
PLAYHOME_MARKER = b"PlayHome"

# Scenario special define
class SpecialScenario(IntEnum):
    # 定義方式：(數值, 顯示名稱)
    NEW = (-1, "新場景")
    SILHOUETTE = (-2, "時光剪影")
    ECHO = (-3, "歲月迴響")

    def __new__(cls, value, label):
        # 因為繼承 IntEnum，我們需要這樣初始化
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        return obj    