# ph-editor/utils/decorators.py
import inspect

from flask import current_app, request
from functools import wraps

from core.shared_data import get_character_file_entry
from utils.exceptions import ConfigError, JSONError, NotFoundError

def require_scan_path(f):
    sig = inspect.signature(f)
    has_scan_path = 'scan_path' in sig.parameters

    @wraps(f)
    def decorated_function(*args, **kwargs):
        path = current_app.config.get("SCAN_PATH")
        if not path:
            raise ConfigError("伺服器配置中未定義 SCAN_PATH")
        
        if has_scan_path:
            kwargs['scan_path'] = path
            
        return f(*args, **kwargs)
    return decorated_function

def inject_character_file_entry(f):
    sig = inspect.signature(f)
    has_sn = 'sn' in sig.parameters
    has_entry = 'entry' in sig.parameters

    @wraps(f)
    def decorated_function(*args, **kwargs):
        sn = kwargs.get('sn') if has_sn else kwargs.pop('sn', None)

        entry = get_character_file_entry(sn)
        if not entry:
            raise NotFoundError(f"找不到 SN: '{sn}' 的資料。")
        
        if has_entry:
            kwargs['entry'] = entry
            
        return f(*args, **kwargs)
    return decorated_function

def require_json_data(f):
    sig = inspect.signature(f)
    wants_data = 'data' in sig.parameters

    @wraps(f)
    def decorated_function(*args, **kwargs):
        json_payload = request.get_json(silent=True)
        
        if json_payload is None:
            raise JSONError()
        
        if wants_data:
            kwargs['data'] = json_payload
            
        return f(*args, **kwargs)
    return decorated_function