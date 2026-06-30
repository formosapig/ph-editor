# ph-editor\utils\input_key

import time
from pynput.keyboard import Key, Controller, KeyCode
# ========== 全域變數 ==========
keyboard = Controller()
is_running = False

# ========== 按鍵對照表 ==========
KEY_MAP = {
    # 方向鍵
    'u': Key.up,
    'd': Key.down,
    'l': Key.left,
    'rt': Key.right,
    
    # 功能鍵
    'pu': Key.page_up,
    'pd': Key.page_down,
    'home': Key.home,
    'end': Key.end,
    
    # 符號鍵（一般字元直接用字串，或用 KeyCode.from_char）
    '.': '.',              # 或者 KeyCode.from_char('.')
    '\\': '\\',            # 反斜線字串
    
    # 小鍵盤（NumPad）的方向鍵與功能鍵
    # 在 pynput 中，小鍵盤數字鍵通常有獨立的 vk (虛擬鍵碼)
    # 如果要精準指定「小鍵盤的 2、4、6、8、5」，建議使用 vk 碼或對應作業系統的特殊常數
    # 這裡以常見的 Windows 虛擬鍵碼 (Virtual Keycodes) 為例：
    '2': KeyCode(vk=98),   # NumPad 2 (Down)
    '4': KeyCode(vk=100),  # NumPad 4 (Left)
    '6': KeyCode(vk=102),  # NumPad 6 (Right)
    '8': KeyCode(vk=104),  # NumPad 8 (Up)
    '5': KeyCode(vk=101),  # NumPad 5 (Clear/Center)
}

# ========== 核心按鍵函式 ==========
def press_key(key_name):
    """單次按壓"""
    key_name_lower = key_name.lower()
    if key_name_lower in KEY_MAP:
        keyboard.press(KEY_MAP[key_name_lower])
        keyboard.release(KEY_MAP[key_name_lower])
        return True
    if len(key_name) == 1:
        keyboard.press(key_name)
        keyboard.release(key_name)
        return True
    return False

def press_and_hold(key_name, duration):
    """按住一段時間"""
    key_name_lower = key_name.lower()
    if key_name_lower in KEY_MAP:
        key_obj = KEY_MAP[key_name_lower]
        keyboard.press(key_obj)
        time.sleep(duration)
        keyboard.release(key_obj)
        return True
    if len(key_name) == 1:
        keyboard.press(key_name)
        time.sleep(duration)
        keyboard.release(key_name)
        return True
    return False

'''
def parse_command(command_str):
    """解析指令字串，回傳動作清單"""
    parts = command_str.strip().split()
    actions = []
    
    for token in parts:
        # 檢查格式：按鍵+數字（例如 r0.3, pageup0.5, num2 0.3）
        if len(token) > 1 and token[-1].isdigit():
            # 從後面找數字部分
            i = len(token) - 1
            while i > 0 and (token[i].isdigit() or token[i] == '.'):
                i -= 1
            key_part = token[:i+1]
            time_part = token[i+1:]
            try:
                hold_seconds = float(time_part)
                actions.append(('hold', key_part, hold_seconds))
                continue
            except ValueError:
                pass
        
        # 單次按壓
        actions.append(('press', token, None))
    
    return actions
'''

def parse_command(command_str):
    """
    解析指令，支援兩種格式：
    1. 舊格式: num20.4  → num2 + 0.4秒 (向後相容)
    2. 新格式: num2@0.4 → num2 + 0.4秒 (更明確)
    3. 純按壓: num2      → 按一下 num2
    """
    parts = command_str.strip().split()
    actions = [('press', 'r', None)] # default press r
    
    for token in parts:
        if not token:
            continue
        
        # ====== 方法1: 檢查 ~ 分隔符 ======
        if '~' in token:
            key_part, time_part = token.split('~', 1)
            try:
                duration = float(time_part)
                if duration > 0:
                    actions.append(('hold', key_part, duration))
                else:
                    actions.append(('press', key_part, None))
                continue
            except ValueError:
                pass  # 解析失敗，繼續嘗試其他方法
                
        # ====== 方法3: 純按壓 ======
        actions.append(('press', token, None))
    
    return actions

def execute_snapshot(command_str, delay=3):
    """
    執行截圖指令（同步，會阻塞）
    回傳執行紀錄
    """
    global is_running
    
    if is_running:
        return "⚠️ 系統忙碌中，請稍候..."
    
    if not command_str or not command_str.strip():
        return "⚠️ 請輸入指令"
    
    is_running = True
    logs = []
    logs.append(f"📥 收到指令：{command_str}")
    
    try:
        # 1. 解析指令
        actions = parse_command(command_str)
        if not actions:
            logs.append("⚠️ 沒有可執行的動作")
            return "\n".join(logs)
        
        # 2. 延遲
        logs.append(f"⏳ 等待 {delay} 秒，請切換到遊戲視窗...")
        time.sleep(delay)
        
        # 3. 執行
        logs.append("🔴 開始執行按鍵序列...")
        for action in actions:
            if action[0] == 'hold':
                _, key, duration = action
                logs.append(f"  ⌨️ 按住 '{key}' 持續 {duration:.2f} 秒")
                success = press_and_hold(key, duration)
                if not success:
                    logs.append(f"  ⚠️ 不支援的按鍵：'{key}'")
                time.sleep(0.1)
            else:
                _, key, _ = action
                logs.append(f"  ⌨️ 按下 '{key}'")
                success = press_key(key)
                if not success:
                    logs.append(f"  ⚠️ 不支援的按鍵：'{key}'")
                time.sleep(0.1)
        
        logs.append("✅ 按鍵序列執行完畢！")
        
    except Exception as e:
        logs.append(f"❌ 錯誤：{str(e)}")
    finally:
        is_running = False
    
    return "\n".join(logs)