# your_character_project/core/character_data.py

import struct
from io import BytesIO

# 從 core/common_types.py 引入通用的讀寫工具
# 假設 common_types.py 包含 _read_bytes, _read_uint32, _read_float,
# 以及 _pack_bytes, _pack_uint32, _pack_float 等
from common_types import _read_bytes, _pack_bytes, _read_uint32, _pack_uint32, _read_float, _pack_float

# 引入所有解析器模組
from parsers import (
    fixed_header_parser,
    hair_parser,
    face_parser,
    body_parser,
    clothing_parser,
    accessory_parser,
    misc_parser
)

# 引入所有序列化器模組
from serializers import (
    fixed_header_serializer,
    hair_serializer,
    face_serializer,
    body_serializer,
    clothing_serializer,
    accessory_serializer,
    misc_serializer
)

class CharacterData:
    """
    用於處理角色二進位資料的核心類別。
    負責解析原始位元組資料、儲存解析後的資料，並提供資料存取和序列化功能。
    """
    def __init__(self, raw_data: bytes):
        """
        初始化 CharacterData 物件，並從原始位元組資料中解析角色資訊。

        Args:
            raw_data: 從 PNG 檔案末尾或其他來源讀取到的原始位元組資料。
        """
        if not isinstance(raw_data, bytes):
            raise TypeError("raw_data 必須是位元組 (bytes) 型別。")

        self.raw_data = raw_data
        # 使用 BytesIO 模擬檔案串流，方便依序讀取和追蹤進度
        self.data_stream = BytesIO(raw_data)
        self.parsed_data = {}  # 儲存解析後的角色資料（Python 字典形式）

        self._parse_all_sections() # 初始化時執行解析

    def _parse_all_sections(self):
        """
        協調所有解析器模組，依序從 data_stream 中解析資料。
        """
        
        debug_mode = False
        
        #print("\n--- 開始解析角色資料 ---")
        try:
            # 1. 解析固定頭部 (30 位元組)
            #print(f"  [偏移: {self.data_stream.tell()}] 解析固定頭部...")
            self.parsed_data['fixed_header'] = fixed_header_parser.parse_fixed_header(self.data_stream, debug_mode)

            # 2. 解析髮型數據
            #print(f"  [偏移: {self.data_stream.tell()}] 解析髮型數據...")
            self.parsed_data['hair'] = hair_parser.parse_hair_data(self.data_stream, debug_mode)

            # 3. 解析臉部數據
            #print(f"  [偏移: {self.data_stream.tell()}] 解析臉部數據...")
            self.parsed_data['face'] = face_parser.parse_face_data(self.data_stream, debug_mode)

            # 4. 解析身體數據
            #print(f"  [偏移: {self.data_stream.tell()}] 解析身體數據...")
            self.parsed_data['body'] = body_parser.parse_body_data(self.data_stream, debug_mode)

            # 5. 解析衣服數據
            #print(f"  [偏移: {self.data_stream.tell()}] 解析衣服數據...")
            self.parsed_data['clothing'] = clothing_parser.parse_clothing_data(self.data_stream, debug_mode)

            # 6. 解析配飾數據
            #print(f"  [偏移: {self.data_stream.tell()}] 解析配飾數據...")
            self.parsed_data['accessory'] = accessory_parser.parse_accessories_data(self.data_stream, debug_mode)

            # 7. 處理散落的無意義數據或未歸類的零碎數據
            # 這裡假設 misc_parser 處理的是一系列分散的數據塊
            # 您需要根據實際結構呼叫多次或在其內部處理
            #print(f"  [偏移: {self.data_stream.tell()}] 解析其他零碎數據/跳過無意義數據...")
            self.parsed_data['misc_data'] = misc_parser.parse_misc_data(self.data_stream, debug_mode)

        except EOFError as e:
            print(f"--- 解析提前結束：資料流末尾意外終止。錯誤: {e} ---")
        except Exception as e:
            print(f"--- 解析過程中發生未知錯誤：{e} ---")
        finally:
            print(f"--- 角色資料解析完成。目前讀取位置: {self.data_stream.tell()} ---")
            #print(f"總原始資料長度: {len(self.raw_data)} 位元組。")
            #print(f"未解析的位元組數: {len(self.raw_data) - self.data_stream.tell()}。")


    def get_data(self) -> dict:
        """
        獲取所有解析後的角色資料。

        Returns:
            包含所有解析數據的字典。
        """
        return self.parsed_data

    def get_value(self, path: list):
        """
        根據路徑獲取特定數據的值。
        例如：get_value(['face', 'nose_height'])

        Args:
            path: 一個列表，表示資料在字典中的層級路徑。

        Returns:
            路徑對應的值，如果路徑不存在則返回 None。
        """
        current_data = self.parsed_data
        for key in path:
            if isinstance(current_data, dict) and key in current_data:
                current_data = current_data[key]
            else:
                return None
        return current_data

    def set_value(self, path: list, new_value):
        """
        根據路徑修改特定數據的值。
        注意：這只修改了記憶體中的 parsed_data，不會自動寫入 raw_data。
        如果要將修改寫回 raw_data，需要呼叫 to_raw_data() 方法。

        Args:
            path: 一個列表，表示資料在字典中的層級路徑。
            new_value: 要設定的新值。

        Returns:
            True 如果修改成功，False 如果路徑不存在或無法修改。
        """
        current_data = self.parsed_data
        for i, key in enumerate(path):
            if i == len(path) - 1: # 找到最後一層，進行修改
                if isinstance(current_data, dict) and key in current_data:
                    current_data[key] = new_value
                    print(f"成功修改路徑 '{'.'.join(path)}' 的值為: {new_value}")
                    return True
                else:
                    print(f"修改失敗: 路徑 '{'.'.join(path)}' 不存在或不是字典。")
                    return False
            else: # 中間層，繼續深入
                if isinstance(current_data, dict) and key in current_data:
                    current_data = current_data[key]
                else:
                    print(f"修改失敗: 路徑 '{'.'.join(path[:i+1])}' 不存在或不是字典。")
                    return False
        return False # 理論上不會執行到這裡

    def to_raw_data(self) -> bytes:
        """
        將目前解析後的資料（parsed_data）序列化回原始位元組資料。
        此方法協調所有序列化器模組來重建位元組串流。

        Returns:
            重建後的位元組資料。
        """
        print("\n--- 開始序列化角色資料 ---")
        output_stream = BytesIO()

        try:
            # 1. 寫入固定頭部
            print(f"  [偏移: {output_stream.tell()}] 序列化固定頭部...")
            fixed_header_serializer.serialize_fixed_header(
                self.parsed_data.get('fixed_header', {}), output_stream
            )

            # 2. 寫入髮型數據
            print(f"  [偏移: {output_stream.tell()}] 序列化髮型數據...")
            hair_serializer.serialize_hair_data(
                self.parsed_data.get('hair', {}), output_stream
            )

            # 3. 寫入臉部數據
            print(f"  [偏移: {output_stream.tell()}] 序列化臉部數據...")
            face_serializer.serialize_face_data(
                self.parsed_data.get('face', {}), output_stream
            )

            # 4. 寫入身體數據
            print(f"  [偏移: {output_stream.tell()}] 序列化身體數據...")
            body_serializer.serialize_body_data(
                self.parsed_data.get('body', {}), output_stream
            )

            # 5. 寫入衣服數據
            print(f"  [偏移: {output_stream.tell()}] 序列化衣服數據...")
            clothing_serializer.serialize_clothing_data(
                self.parsed_data.get('clothing', {}), output_stream
            )

            # 6. 寫入配飾數據
            print(f"  [偏移: {output_stream.tell()}] 序列化配飾數據...")
            accessory_serializer.serialize_accessory_data(
                self.parsed_data.get('accessory', {}), output_stream
            )

            # 7. 寫入其他零碎數據/填充無意義數據
            print(f"  [偏移: {output_stream.tell()}] 序列化其他零碎數據/填充無意義數據...")
            misc_serializer.serialize_misc_data(
                self.parsed_data.get('misc_data', {}), output_stream
            )

        except Exception as e:
            print(f"--- 序列化過程中發生錯誤：{e} ---")
            # 根據需求，這裡可以選擇返回部分數據或重新拋出錯誤
            return b'' # 返回空位元組表示失敗

        final_bytes = output_stream.getvalue()
        print(f"--- 角色資料序列化完成。總輸出位元組數: {len(final_bytes)} ---")
        return final_bytes