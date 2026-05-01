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

class InvalidOperationError(APIError):
    """
    當用戶嘗試執行邏輯上不合理的操作時拋出。
    例如：對數值欄位進行字串特定的排序、對已關閉的案子進行修改等。
    """
    def __init__(self, message="此操作在當前上下文中無效"):
        super().__init__(message, status_code=422) # 422 常用於語義邏輯錯誤
        
class NoUpdateRequired(APIError):
    """
    當前端請求更新，但後端判斷不需要改動資料時拋出。
    使用 204 No Content，這在 Fetch API 中代表請求成功但無回傳值。
    """
    def __init__(self, message="No update required"):
        super().__init__(message, status_code=204)
