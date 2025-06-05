# ph-editor
專為 PH 遊戲打造的女角編輯工具，支持髮型、臉部、身體等數據編輯

## 功能

- 解析遊戲角色二進位資料並轉成 JSON
- 編輯角色各種屬性（髮型、臉部、身體、服裝等）
- 將修改後的資料重新序列化成遊戲可讀格式
- 提供簡易的 Web 介面與 API

## 安裝及執行 Installation and Usage

下載後直接執行 `python app.py`。

預設會在本機的 `localhost:5000` 開啟網頁，並自動啟動瀏覽器。

請先點選介面最左邊的資料夾圖示，然後輸入你本地端的角色存檔資料夾路徑。

---

Run `python app.py` after downloading.

By default, the web interface will be available at `localhost:5000` and will open automatically in your web browser.

First, click the folder icon on the far left of the interface, then enter the path to your local character save files folder.

## 專案結構

game_data/ 角色資料對照表

parsers/ — 各類資料解析模組

serializers/ — 資料序列化模組

static/ — 前端靜態資源（JS、CSS、圖片）

templates/ — HTML 模板

app.py — Flask 主要入口

## 授權
本專案使用 MIT 授權，歡迎自由使用與修改。

## 免責聲明 Disclaimer
中文：

本軟體僅用於編輯 PlayHome 女性角色存檔，遊戲本體及相關資源請自行合法取得。遊戲版權及圖片皆屬遊戲公司所有。本軟體以「現狀」提供，作者不保證軟體無錯誤，也不對使用本軟體所造成的任何直接、間接、附帶或衍生的損害負責。使用者自行承擔使用風險。

English:

This software is intended solely for editing PlayHome female character save files. Please obtain the game and related resources legally by yourself. All copyrights and images belong to the game company. This software is provided "as-is", without any express or implied warranty. The author makes no guarantees about the correctness or reliability of this software, and is not liable for any direct, indirect, incidental, or consequential damages arising from its use. Use at your own risk.
