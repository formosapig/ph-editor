# ph-editor/serializers/clothing_serializer.py

from io import BytesIO
import json
from utils.common_types import (
    _pack_uint32, _pack_int32, _pack_uint8, _pack_float, _pack_color, _parse_and_pack_float
)
# clothing data
from game_data.clothing_data import (
    get_clothing_by_id,
    is_colorful,
    is_disabled,
    is_cut_clothing,
    has_option,
    get_option_flags
)

# 從 body_parser.py 借用過來的浮點數轉換函式 (反向操作)
def _parse_percentage_to_float(value: int, scale: float = 100) -> float:
    """
    將 0-100% 的整數值轉換為浮點數。
    """
    return value / scale

def serialize_clothing_item(stream: BytesIO, item_data: dict, slot: str, debug_mode: bool = False) -> None:
    """
    序列化單一服裝配件的數據，直接寫入到傳入的 stream 中。
    Args:
        stream: 要寫入序列化數據的 BytesIO 串流物件。
        item_data: 包含服裝數據的字典。
        slot: 當前序列化的服裝配件槽位名稱。
        debug_mode: 是否開啟除錯模式，印出詳細序列化過程。
    """
    slot_idx = item_data.get('slot', 0)
    item_id = item_data.get('id', 0)
    color_flag = item_data.get('color', 0) # 預設為 0，表示不可換色

    if debug_mode:
        print(f"    [Offset: {stream.tell()}] Serializing '{slot}' data (ID: {item_id}).")

    # 寫入 ID、extra 和 color_flag
    stream.write(_pack_int32(slot_idx))
    stream.write(_pack_int32(item_id))
    stream.write(_pack_int32(color_flag)) # 寫入 color_flag

    # 如果 color_flag 為 3，則寫入顏色和光澤屬性
    if color_flag == 3:
        if debug_mode: print(f"        [Offset: {stream.tell()}] Serializing color data.")
        stream.write(_pack_color(item_data.get('main_color', '(0, 0, 0, 255)')))
        stream.write(_pack_color(item_data.get('main_shine', '(0, 0, 0, 0)')))
        stream.write(_parse_and_pack_float(item_data.get('main_shine_strength', 0)))
        stream.write(_parse_and_pack_float(item_data.get('main_shine_texture', 0)))

        stream.write(_pack_color(item_data.get('sub_color', '(0, 0, 0, 255)')))
        stream.write(_pack_color(item_data.get('sub_shine_color', '(0, 0, 0, 0)')))
        stream.write(_parse_and_pack_float(item_data.get('sub_shine_strength', 0)))
        stream.write(_parse_and_pack_float(item_data.get('sub_shine_texture', 0)))
    
    # 泳裝的 option flags 在 parse 時會加入，序列化時不需要特別處理，因為它們會從後面的 1 byte 讀取

def serialize_clothing_data(clothing_data: dict, stream: BytesIO, debug_mode: bool = False):
    """
    序列化角色的服裝數據，直接寫入到傳入的 stream 中。
    Args:
        stream: 要寫入序列化數據的 BytesIO 串流物件。
        clothing_data: 包含服裝數據的字典。
        debug_mode: 是否開啟除錯模式，印出詳細序列化過程。
    """
    if debug_mode:
        print(f"  [Offset: {stream.tell()}] Starting to serialize clothing data.")

    try:
        # 依照 parse 的順序進行序列化，並直接寫入 stream
        serialize_clothing_item(stream, clothing_data.get('top', {}), "top", debug_mode)
        if debug_mode: print(f"    [Offset: {stream.tell()}] End of Top data serialization.")

        serialize_clothing_item(stream, clothing_data.get('bottom', {}), "bottom", debug_mode)
        if debug_mode: print(f"    [Offset: {stream.tell()}] End of Bottom data serialization.")

        serialize_clothing_item(stream, clothing_data.get('bra', {}), "bra", debug_mode)
        if debug_mode: print(f"    [Offset: {stream.tell()}] End of Bra data serialization.")

        serialize_clothing_item(stream, clothing_data.get('panty', {}), "panty", debug_mode)
        if debug_mode: print(f"    [Offset: {stream.tell()}] End of Panty data serialization.")

        serialize_clothing_item(stream, clothing_data.get('swimsuit', {}), "swimsuit", debug_mode)
        if debug_mode: print(f"    [Offset: {stream.tell()}] End of Swimsuit (Full) data serialization.")

        serialize_clothing_item(stream, clothing_data.get('swimsuit_top', {}), "swimsuit_top", debug_mode)
        if debug_mode: print(f"    [Offset: {stream.tell()}] End of Swimsuit Top data serialization.")

        serialize_clothing_item(stream, clothing_data.get('swimsuit_bottom', {}), "swimsuit_bottom", debug_mode)
        if debug_mode: print(f"    [Offset: {stream.tell()}] End of Swimsuit Bottom data serialization.")

        serialize_clothing_item(stream, clothing_data.get('gloves', {}), "gloves", debug_mode)
        if debug_mode: print(f"    [Offset: {stream.tell()}] End of Gloves data serialization.")

        serialize_clothing_item(stream, clothing_data.get('pantyhose', {}), "pantyhose", debug_mode)
        if debug_mode: print(f"    [Offset: {stream.tell()}] End of Pantyhose data serialization.")

        serialize_clothing_item(stream, clothing_data.get('socks', {}), "socks", debug_mode)
        if debug_mode: print(f"    [Offset: {stream.tell()}] End of Socks data serialization.")

        serialize_clothing_item(stream, clothing_data.get('shoes', {}), "shoes", debug_mode)
        if debug_mode: print(f"    [Offset: {stream.tell()}] End of Shoes data serialization.")

        # 序列化 clothing_set, option_top, option_bottom
        clothing_type_val = 0 if clothing_data.get('clothing_set') == '通常' else 1
        stream.write(_pack_uint8(clothing_type_val))

        option_top_val = 1 if clothing_data.get('swimsuit', {}).get('option_top') == 'on' else 0
        option_bottom_val = 1 if clothing_data.get('swimsuit', {}).get('option_bottom') == 'on' else 0

        stream.write(_pack_uint8(option_top_val))
        stream.write(_pack_uint8(option_bottom_val))

    except Exception as e:
        if debug_mode:
            print(f"  [ERROR] Error occurred during clothing data serialization: {e}")
        raise

    if debug_mode:
        print(f"  Clothing data serialization complete. Current stream position: {stream.tell()}")
        # 因為是直接寫入 stream，這裡不會有完整的 json_output 或 bytes_output 供檢查
        # 如果需要檢查，可能需要在函數外部呼叫 stream.getvalue()