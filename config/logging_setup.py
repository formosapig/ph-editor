# config/logging_setup.py
import logging
import os

from colorlog import ColoredFormatter


def setup_logging():
    """設定應用程式的日誌系統。"""

    BASE_DIR = os.getcwd()

    class RelativePathColoredFormatter(ColoredFormatter):
        def format(self, record):
            pathname = record.pathname
            # 確保路徑處理在 Windows 和 Linux 上都適用
            # 這裡簡單處理為移除 BASE_DIR 的部分
            if pathname.startswith(BASE_DIR):
                relative_path = pathname[len(BASE_DIR) + 1 :]
                record.pathname = relative_path
            return super().format(record)

    handler = logging.StreamHandler()
    formatter = RelativePathColoredFormatter(
        "%(log_color)s[%(levelname)s] (%(pathname)s:%(lineno)d) → %(message)s\n",
        log_colors={
            "DEBUG": "white",  # 您選擇的白色
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )
    handler.setFormatter(formatter)

    # 取得根日誌器，並設定其級別和處理器
    # 這樣所有通過 logging.getLogger() 取得的日誌器都會繼承這些設定
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # 您的應用程式總體日誌級別

    # 清空現有的 handlers，確保只使用我們設定的
    if not root_logger.handlers:  # 避免重複添加 handler
        root_logger.addHandler(handler)

    # 設定 PIL 函式庫的 logger 為 WARNING 或 INFO，以減少其詳細輸出
    # 這裡設置為 WARNING，表示只顯示 WARNING 及更高層級的 PIL 訊息
    logging.getLogger("PIL").setLevel(logging.WARNING)

    # 將 Werkzeug 的日誌級別設定為 WARNING 或 ERROR
    # WARNING 會顯示警告和錯誤，ERROR 只顯示錯誤
    # 304 訊息屬於 INFO 級別，所以設定為 WARNING 或 ERROR 就不會顯示了
    logging.getLogger("werkzeug").setLevel(logging.WARNING)

    #logging.info("日誌系統設定完成。")
