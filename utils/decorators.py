# ph-editor/utils/decorators.py
from flask import current_app, jsonify
from functools import wraps

def require_scan_path(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 只要這是在處理 API 請求，current_app 就會自動指向你的 App
        path = current_app.config.get("SCAN_PATH")
        if not path:
            return jsonify({"error": "SCAN_PATH not set"}), 500
        
        # 檢查 f 是否真的想要這個參數
        import inspect
        sig = inspect.signature(f)
        if 'scan_path' in sig.parameters:
            kwargs['scan_path'] = path
            
        return f(*args, **kwargs)
    return decorated_function