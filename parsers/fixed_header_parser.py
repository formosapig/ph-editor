# ph-editor/parsers/fixed_header_parser.py
import json
import logging
from io import BytesIO

from utils.common_types import _read_bytes, _read_uint8, _read_uint32

logger = logging.getLogger(__name__)
logger.disabled = True


def parse_fixed_header(
    stream: BytesIO, debug_mode: bool = False
) -> dict:  # 加上 debug_mode 參數
    """
    解析角色資料的固定頭部 (約 30 位元組)。
    此函式會從提供的 BytesIO 串流中讀取資料，並返回一個字典。

    Args:
        stream: 包含角色二進位資料的 BytesIO 串流物件。
        debug_mode: 布林值，如果為 True 則會列印除錯訊息。

    Returns:
        一個字典，包含解析後的固定頭部數據。
    """
    fixed_header_data = {}
    current_pos = stream.tell()
    if debug_mode:  # 使用 debug_mode 控制輸出
        print(f"    [偏移: {current_pos}] 開始解析固定頭部。")

    try:
        # 讀取 PlayHome_Female
        mark_bytes = _read_bytes(stream, 15)
        fixed_header_data["mark"] = mark_bytes.decode("ascii")
        logger.debug(f"標記: {fixed_header_data['mark']}")

        # 讀取 怪異符號 4 bytes
        strange_bytes = _read_bytes(stream, 4)
        fixed_header_data["strange"] = strange_bytes.decode("utf-8")
        logger.debug(f"怪異: {fixed_header_data['strange']}")

        # 7 bytes 對齊
        _read_bytes(stream, 7)

        # 版本號
        fixed_header_data["version"] = _read_uint32(stream)
        logger.debug(f"版本: {fixed_header_data['version']}")

    except EOFError as e:
        if debug_mode:
            print(f"    [錯誤] 解析固定頭部時遇到資料流提前結束: {e}")
        raise
    except Exception as e:
        if debug_mode:
            print(f"    [錯誤] 解析固定頭部時發生未知錯誤: {e}")
        raise

    if debug_mode:
        print(f"    固定頭部解析完成。下一個讀取位置: {stream.tell()}")
        # --- 除錯：在解析器內部直接嘗試 JSON 轉換 ---
        try:
            json_output = json.dumps(fixed_header_data, indent=2)
            print("\n    --- fixed_header_parser JSON 除錯輸出 ---")
            print(json_output)
            print("    -------------------------------------------\n")
        except TypeError as json_e:
            print(
                f"\n    [重要錯誤] fixed_header_parser 返回的數據無法 JSON 序列化: {json_e}"
            )
            print(
                f"    未序列化數據類型: {[type(v) for v in fixed_header_data.values() if isinstance(v, (bytes, bytearray))]}"
            )
            print("    -------------------------------------------\n")
        # --- 除錯結束 ---

    return fixed_header_data
