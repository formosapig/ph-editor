# ph-editor/parsers/accessory_parser.py

import json
from io import BytesIO

# accessory data
from game_data.accessory_data import (
    get_accessory_by_id,
    get_slot_name,
    get_type_name,
    is_colorful,
)
from utils.common_types import (
    _read_and_format_color,
    _read_and_format_to_value,
    _read_bytes_as_hex,
    _read_float,
    _read_int32,
)


def parse_accessory_item(
    stream: BytesIO, slot_index: int, debug_mode: bool = False
) -> dict:
    """
    解析單一配飾的數據，包括 ID、顏色和光澤屬性。
    Args:
        stream: 包含角色二進位資料的 BytesIO 串流物件。
        slot_index: 當前解析的配飾槽位索引 (0-9)，用於除錯輸出。
        debug_mode: 是否開啟除錯模式，印出詳細解析過程。
    Returns:
        一個字典，包含解析後的配飾數據。
    """
    start_offset = stream.tell()

    if debug_mode:
        print(
            f"    [Offset: {start_offset}] Parsing accessory item for slot {slot_index}."
        )

    # 讀取基本屬性
    accessory_type = _read_int32(stream)  # -1 = 無
    accessory_id = _read_int32(stream)
    accessory_slot = _read_int32(stream)

    part = {
        "#info": f"[{get_slot_name(accessory_slot)}]→{get_type_name(accessory_type)}:{get_accessory_by_id(accessory_type, accessory_id)}",
        "type": accessory_type,
        "id": accessory_id,
        "slot": accessory_slot,
        "position": {
            "x": _read_float(stream),
            "y": _read_float(stream),
            "z": _read_float(stream),
        },
        "rotation": {
            "x": _read_float(stream),
            "y": _read_float(stream),
            "z": _read_float(stream),
        },
        "scale": {
            "x": _read_float(stream),
            "y": _read_float(stream),
            "z": _read_float(stream),
        },
    }

    part["!color_mark"] = _read_bytes_as_hex(stream, 4)

    # print(f"SlotIndex: {slot_index}, id: ({accessory_id[0]}, {accessory_id[1]}), gap: {part['gap']}")

    # 讀取顏色和光澤屬性 (如果可換色), 跟 配飾的顏色無關, 根據 gap 來決定是不是要讀額外顏色資料...
    # if is_colorful(accessory_id) > 0 and part['gap'] == '03 00 00 00':
    # 看起來是只用 gap 去決定
    if part["!color_mark"] == "03 00 00 00":
        part.update(
            {
                "main_color": _read_and_format_color(stream),
                "main_shine": _read_and_format_color(stream),
                "main_strength": _read_and_format_to_value(stream),
                "main_texture": _read_and_format_to_value(stream),
                "sub_color": _read_and_format_color(stream),
                "sub_shine": _read_and_format_color(stream),
                "sub_strength": _read_and_format_to_value(stream),
                "sub_texture": _read_and_format_to_value(stream),
            }
        )

    if debug_mode:
        print(
            f"    [Offset: {stream.tell()}] Finished parsing accessory item for slot {slot_index}."
        )

    return part


def parse_accessories_data(stream: BytesIO, debug_mode: bool = False) -> dict:
    """
    解析角色的配飾數據。
    Args:
        stream: 包含角色二進位資料的 BytesIO 串流物件。
        debug_mode: 是否開啟除錯模式，印出詳細解析過程。
    Returns:
        一個字典，包含解析後的配飾數據和剩餘的位元組長度。
    """
    accessories_data = {}

    if debug_mode:
        current_pos = stream.tell()
        print(f"  [Offset: {current_pos}] Starting to parse accessories data.")
        print(
            f"  Expected single accessory block length: {SINGLE_ACCESSORY_BLOCK_LENGTH} bytes."
        )

    try:
        # 先讀取開頭的 4 bytes padding (0x08AE)
        # stream.seek(0x08AE) # 如果檔案開頭不是從這裡開始讀取，則需要seek
        # accessories_data['start'] = _read_bytes_as_hex(stream, 16) # 0x08AE padding
        if debug_mode:
            print(
                f"    [Offset: {stream.tell()}] Read 4 bytes padding after clothing data."
            )

        # 解析 10 個配飾槽位
        for i in range(10):  # 10 個槽位，從 0 到 9
            accessories_data[f"accessory_{i+1:02}"] = parse_accessory_item(
                stream, i, debug_mode
            )

    except EOFError as e:
        if debug_mode:
            print(
                f"    [ERROR] Stream ended prematurely when parsing accessories data: {e}"
            )
        raise
    except Exception as e:
        if debug_mode:
            print(
                f"    [ERROR] Unknown error occurred when parsing accessories data: {e}"
            )
        raise
    finally:
        # 計算並儲存剩餘的位元組長度
        accessories_data["least_bytes"] = len(stream.getvalue()) - stream.tell()
        if debug_mode:
            print(
                f"  Accessories data parsing complete. Next read position: {stream.tell()}"
            )
            print(f"  Least bytes remaining: {accessories_data['least_bytes']}")

            try:
                json_output = json.dumps(accessories_data, indent=2, ensure_ascii=False)
                print("\n  --- Accessories Parser JSON Debug Output ---")
                print(json_output)
                print("  -----------------------------------\n")
            except TypeError as json_e:
                print(
                    f"\n  [CRITICAL ERROR] Accessories parser returned data cannot be JSON serialized: {json_e}"
                )
                problematic_types = []

                def find_unserializable_in_dict(d):
                    for k, v in d.items():
                        if isinstance(v, (bytes, bytearray)):
                            problematic_types.append(f"Key '{k}': {type(v)}")
                        elif isinstance(v, dict):
                            find_unserializable_in_dict(v)

                find_unserializable_in_dict(accessories_data)
                print(f"  Unserializable data types: {problematic_types}")
                print("  -----------------------------------\n")

    return accessories_data
