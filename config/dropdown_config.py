# ph-editor/config/dropdown_config.py

dropdown_config_map = {
    ('face', 'overall'): [
        {
            "displayLabel": "臉部輪廓",
            "dataKey": "contour_id",     # ← parsed data 的 key
            "labelKey": "#contour_name", # ← parsed data 的 comment
            "module": "face_data",
            "attribute": "FACE_DETAILS",
            "subKey": "contour",       # ← 指定要讀取的欄位
            "lang": "zh"               # ← 指定顯示語言
        },
        {
            "displayLabel": "臉部肌肉",
            "dataKey": "muscle_id",
            "labelKey": "#muscle_name", # ← parsed data 的 comment
            "module": "face_data",
            "attribute": "FACE_DETAILS",
            "subKey": "muscle",       # ← 指定要讀取的欄位
            "lang": "zh"               # ← 指定顯示語言
        },
        {
            "displayLabel": "臉部皺紋",
            "dataKey": "wrinkle_id",
            "labelKey": "#wrinkle_name", # ← parsed data 的 comment
            "module": "face_data",
            "attribute": "FACE_DETAILS",
            "subKey": "wrinkle",       # ← 指定要讀取的欄位
            "lang": "zh"               # ← 指定顯示語言
        }
    ]
}