# PH Character Editor (Unofficial)
⚠️ **非官方** PlayHome 女性角色存檔編輯工具（研究用途）

## 功能 (Current Features)
- ✅ **解析**：將遊戲二進制角色數據轉換為可讀的 JSON 結構
- ✏️ **編輯**：修改髮型、臉部、身體參數（支援實時預覽）
- ⚠️ **實驗性**：序列化回遊戲格式（穩定性待測試）
- 🌐 **Web 介面**：基於 Flask 的輕量級操作界面

## 安裝及執行 Installation and Usage

### 基本需求
- Python 3.8+
- 依賴庫：`pip install -r requirements.txt`

1. `pip install -r requirements.txt`  
2. `python app.py`  
3. ｂｒｏｗｓｅｒ　`http://localhost:5000`  

## 專案結構

game_data/ 角色資料對照表

parsers/ — 各類資料解析模組

serializers/ — 資料序列化模組

static/ — 前端靜態資源（JS、CSS、圖片）

templates/ — HTML 模板

app.py — Flask 主要入口

## 授權
本專案使用 MIT 授權，歡迎自由使用與修改。

## 免責聲明 (Disclaimer)
### 版權與責任
- 本工具與遊戲開發商 **Illusion** 無關，所有遊戲資產版權歸原公司所有。  
- 使用者應合法取得遊戲副本，禁止用於盜版或商業用途。  

### 風險自擔
- 此工具可能導致存檔損壞，使用前務必備份。  
- 作者不對數據丟失或遊戲兼容性問題負責。  

### 合理使用
- 僅限於個人研究與模組開發，禁止用於製作/傳播成人內容。

## Disclaimer (English Version)
###　Copyright Notice
—　This is an unofficial tool for PlayHome character data modification.

—　All game assets, trademarks, and copyrights belong to ILLUSION and/or its respective owners.

—　Users must legally own a copy of PlayHome to use this software.

### Limitation of Liability
⚠️ Use at your own risk.

- This tool may corrupt save files. Always back up original files before editing.

- The author provides no warranty for data loss, game compatibility, or unintended effects.

- The software is offered "as-is," and the author disclaims all responsibility for direct/indirect damages.

### Usage Restrictions
- Permitted: Personal research, non-commercial modding, and interoperability studies.

- Prohibited:

-- Reverse engineering for piracy or cheating.

Distribution of modified game assets violating ILLUSION's terms.

Creation/distribution of adult content using this tool.

### Project Status
- This is a community-driven project unaffiliated with ILLUSION.

- Features marked experimental (e.g., save serialization) may be unstable.