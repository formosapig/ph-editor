# ph-editor/utils/exceptions.py
class APIError(Exception):
    """
    自定義 API 異常基底類別。
    用法: raise APIError("訊息", 404)
    """
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class NotFoundError(APIError):
    def __init__(self, message="Resource not found"):
        super().__init__(message, status_code=404)

class ValidationError(APIError):
    def __init__(self, message="Invalid input data"):
        super().__init__(message, status_code=400)

class ConfigError(APIError):
    def __init__(self, message="Server configuration error"):
        super().__init__(message, status_code=500)

class ErrorTest(APIError):
    def __init__(self, message="錯誤測試。"):
        super().__init__(message, status_code=500)

class JSONError(APIError):
    def __init__(self, message="無效的 json 格式。"):
        super().__init__(message, status_code=400)
