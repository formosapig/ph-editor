from flask import Blueprint, request, render_template, jsonify, current_app, session, Response
import os
import json
import base64
import traceback

# 從 shared_data 模組引入 get_character_data 和 PLAYHOME_MARKER
# get_character_data 會處理延遲解析邏輯
from shared_data import get_character_data, PLAYHOME_MARKER, add_or_update_character 

edit_bp = Blueprint('edit_bp', __name__)


# 假設您有一個 function 來讀取、解析和儲存檔案
def process_file(file_name):
    print("process file")
    try:
        scan_path = current_app.config['SCAN_PATH']
        file_name_with_ext = file_name if file_name.lower().endswith('.png') else file_name + '.png'
        file_path = os.path.join(scan_path, file_name_with_ext)

        print(f"🧾 嘗試讀取檔案: {file_path}")
        with open(file_path, 'rb') as f:
            full_png_data = f.read()

        print("📦 檔案讀取成功，搜尋 PLAYHOME_MARKER")

        marker_start_pos = full_png_data.find(PLAYHOME_MARKER)
        if marker_start_pos == -1:
            print("❌ 未找到 PLAYHOME_MARKER")
            return jsonify({"error": f"檔案 '{file_name}' 中未找到 PlayHome 標記，無法解析角色數據。"}), 400

        raw_character_data_with_marker = full_png_data[marker_start_pos:]
        print("✅ 找到 marker，呼叫 add_or_update_character()")

        add_or_update_character(file_name, raw_character_data_with_marker)

        print("✅ 更新角色成功，準備從 DB 取得資料")
        character_data_obj = get_character_data(file_name)

        if not character_data_obj:
            print("❌ get_character_data() 回傳 None")
            return jsonify({"error": f"雖然成功讀取檔案，但解析後仍無法取得角色數據: {file_name}。"}), 500

        return character_data_obj.get_data()

    except FileNotFoundError:
        print("❗ 檔案不存在")
        return jsonify({"error": "檔案不存在。", "parsed_data_preview": "無"}), 404

    except Exception as e:
        print("❌ 未知例外:\n%s", traceback.format_exc())
        return jsonify({"error": f"讀取角色檔案時發生錯誤: {e}"}), 500

@edit_bp.route('/edit')
def edit():
    """
    編輯角色資料的路由。
    接收 'file' 參數（即 character_id），從共享數據庫中獲取 CharacterData 物件。
    若資料不存在，將嘗試從角色圖檔中讀取並回存至共享資料庫。
    """
    file_name = request.args.get('file')  # 這裡的 file_name 就是 character_id
    if not file_name:
        return "缺少檔案名稱，請提供一個角色 ID。", 400

    # 嘗試從 shared_data 中獲取資料
    character_data_obj = get_character_data(file_name)

    if not character_data_obj:
        # 若資料不存在，嘗試從圖檔讀取
        try:
            scan_path = current_app.config['SCAN_PATH']
            
            # 加上 .png 副檔名（若尚未附上）
            file_name_with_ext = file_name if file_name.lower().endswith('.png') else file_name + '.png'
            file_path = os.path.join(scan_path, file_name_with_ext)
            
            with open(file_path, 'rb') as f:
                full_png_data = f.read()

            marker_start_pos = full_png_data.find(PLAYHOME_MARKER)
            if marker_start_pos == -1:
                return f"檔案 '{file_name}' 中未找到 PlayHome 標記，無法解析角色數據。", 400

            raw_character_data_with_marker = full_png_data[marker_start_pos:]
            add_or_update_character(file_name, raw_character_data_with_marker)  # 儲存到共享資料庫

            # 再次從 DB 取得資料
            character_data_obj = get_character_data(file_name)
            if not character_data_obj:
                return f"雖然成功讀取檔案，但解析後仍無法取得角色數據: {file_name}。", 500

        except Exception as e:
            return f"讀取角色檔案時發生錯誤: {e}", 500

    # 將解析後的數據（字典形式）傳給前端
    content_for_frontend = character_data_obj.get_data()
    session['current_edit_character_id'] = file_name
    return render_template('edit.html', file=file_name, data=json.dumps(content_for_frontend))

# 新增的重讀檔案路由
@edit_bp.route('/edit/reload_file', methods=['GET'])
def reload_file():
    character_id = session.get('current_edit_character_id')
    print(f"character_id: {character_id}")
    if not character_id:
        return jsonify({'error': '尚未載入角色或會話數據丟失，請先載入角色。'}), 400
        
    try:
        # **重新讀取檔案、解析並回存**
        processed_data = process_file(character_id) # 重新調用處理檔案的 function

        return Response(
            json.dumps(processed_data, ensure_ascii=False, indent=2),  # 保留順序 + pretty print
            content_type='application/json'
        )
    except Exception as e:
        return jsonify({"error": f"重讀檔案失敗: {str(e)}", "parsed_data_preview": "無"}), 500


@edit_bp.route('/edit/save', methods=['POST'])
def save_edit():
    """
    保存角色編輯數據的路由。
    接收前端 POST 過來的 JSON 數據，更新 CharacterData 物件，並將更改寫回原始 PNG 檔案。
    """
    data = request.get_json()
    updated_parsed_data = data.get('content') # 從前端獲取更新後的解析數據

    # 從 Session 中獲取當前正在編輯的角色 ID。
    character_id = session.get('current_edit_character_id')

    if not character_id or not updated_parsed_data:
        return jsonify({'error': '會話數據丟失或缺少更新內容，請重新載入角色。'}), 400

    # 從 shared_data 獲取 CharacterData 物件。
    # 這裡會確保 CharacterData 物件已經被載入和解析。
    character_data_obj = get_character_data(character_id)
    if not character_data_obj:
        return jsonify({'error': f"找不到要保存的角色數據: {character_id}。請重新載入檔案。"}), 404

    try:
        # 更新 CharacterData 物件內部儲存的解析數據。
        # 由於 CharacterData 物件是通過引用從 shared_data 取得的，這個修改會直接反映到共享的實例上。
        character_data_obj.parsed_data = updated_parsed_data 

        # 將更新後的 CharacterData 物件序列化回新的原始二進位數據。
        new_raw_character_data_with_marker = character_data_obj.to_raw_data()

        # 構建檔案的完整路徑。
        file_name_with_ext = character_id + '.png'
        # 假設你的 'SCAN_PATH' 已經在 app.py 中被正確設置和更新。
        file_path = os.path.join(current_app.config.get('SCAN_PATH'), file_name_with_ext)

        # 讀取原始 PNG 檔案的整個內容，以便替換其中的自定義數據。
        with open(file_path, 'rb') as f:
            full_png_data = f.read()

        # 找到 'PlayHome' 標記的起始位置。
        marker_start_pos = full_png_data.find(PLAYHOME_MARKER)

        if marker_start_pos == -1:
            return jsonify({'error': f"檔案中未找到 '{PLAYHOME_MARKER.decode()}' 標記，無法保存數據。"}), 400

        # 重建完整的 PNG 數據：PNG 前半部分 + 新的自定義數據。
        # 這裡假設自定義數據從 PlayHome 標記開始，一直到 PNG 檔案的末尾。
        png_prefix = full_png_data[:marker_start_pos]
        updated_full_png_data = png_prefix + new_raw_character_data_with_marker

        # 將更新後的數據寫回檔案（二進位模式）。
        with open(file_path, 'wb') as f:
            f.write(updated_full_png_data)

        return jsonify({'success': True, 'message': '數據保存成功！'})
    except Exception as e:
        print(f"保存檔案時發生錯誤: {e}")
        return jsonify({'error': f"保存失敗: {str(e)}"}), 500


@edit_bp.route('/edit/read_hex', methods=['GET'])
def read_hex():
    """
    讀取並返回角色數據的十六進位表示和完整的解析結果。
    這對於除錯和驗證數據非常有用。
    """
    character_id = session.get('current_edit_character_id')
    if not character_id:
        return jsonify({'error': '尚未載入角色或會話數據丟失，請先載入角色。'}), 400

    character_data_obj = get_character_data(character_id)
    if not character_data_obj:
        return jsonify({'error': f"找不到角色數據: {character_id}。請重新載入檔案。"}), 400

    # 顯示 CharacterData 實例接收到的原始數據的前 100 個位元組（包含 PlayHome 標記）。
    display_length = 100
    hex_to_show = character_data_obj.raw_data[:display_length]
    hex_str = ' '.join(f'{b:02X}' for b in hex_to_show)
    if len(character_data_obj.raw_data) > display_length:
        hex_str += " ..."
        
    # 獲取解析後的完整數據字典
    parsed_data = character_data_obj.get_data()

    # 將整個 parsed_data 字典轉換為 JSON 字串
    # indent=2 參數可以讓 JSON 輸出格式化，更易讀
    try:
        parsed_data_json_str = json.dumps(parsed_data, indent=2, ensure_ascii=False) # ensure_ascii=False 允許顯示中文
    except TypeError as e:
        # 如果 parsed_data 中仍然存在無法序列化的類型，這裡會捕獲錯誤
        return jsonify({'error': f"解析後的數據無法 JSON 序列化: {e}。請檢查解析器中是否有 bytes 或其他非 JSON 類型。",
                        'parsed_data_preview': str(parsed_data)[:500] + '...'}), 500

    # 返回 JSON 格式的除錯資訊。
    return jsonify({
        'raw_data_hex_preview': f"--- 原始數據前 {display_length} 位元組 (包含 '{PLAYHOME_MARKER.decode()}' 標記) ---\n{hex_str}",
        'full_parsed_data': parsed_data_json_str # 直接返回整個解析後的數據的 JSON 字串
    })