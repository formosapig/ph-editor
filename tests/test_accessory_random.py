# ph-editor/tests/test_accessory_random.py

import random
from io import BytesIO

import pytest

# 導入配飾數據
from game_data.accessory_data import (
    ACCESSORY_ITEMS,
    ACCESSORY_SLOT,
    ACCESSORY_TYPE,
    C0,
    C1,
    C2,
    C3,
)
from parsers.accessory_parser import parse_accessories_data

# 導入序列化和解析函數
from serializers.accessory_serializer import serialize_accessories_data

# test utils - Assuming these are available in tests/utils.py
from tests.utils import (  # _random_hex_string is not directly used for data generation but for internal checks
    _random_color_str,
    compare_dicts,
)


def _random_float_small() -> float:
    """Generates a random float value for position, rotation, or scale."""
    return random.uniform(-5.0, 5.0)


def format_accessory_for_test() -> dict:
    """
    Constructs a dictionary representing a single accessory item with random or default values.
    This structure is designed to be serialized and then parsed back for roundtrip testing.
    """
    # Randomly select an accessory item, including the "なし" (None) item sometimes
    # to test empty slots/items.
    item = random.choice(ACCESSORY_ITEMS)

    accessory_type_id = item["id"][0]
    accessory_item_id = item["id"][1]
    # Get the color flag from the item definition, default to C0 if not specified
    color_flag = item.get("flag", C0)

    # Randomly select a valid accessory slot ID from the ACCESSORY_SLOT definitions.
    # The parser reads this directly from the stream.
    random_slot_id = random.choice([s["id"] for s in ACCESSORY_SLOT])

    formatted_data = {
        # '#info' is added by the parser, not part of the serialized data, so not included here.
        "type": accessory_type_id,
        "id": accessory_item_id,
        "slot": random_slot_id,
        "position": {
            "x": _random_float_small(),
            "y": _random_float_small(),
            "z": _random_float_small(),
        },
        "rotation": {
            "x": _random_float_small(),
            "y": _random_float_small(),
            "z": _random_float_small(),
        },
        "scale": {
            "x": _random_float_small(),
            "y": _random_float_small(),
            "z": _random_float_small(),
        },
    }

    # The accessory parser's logic for reading conditional color data is *solely* based on
    # the '!color_mark' field being '03 00 00 00'. It does not use the `is_colorful` flag
    # from `accessory_data` to decide whether to read these bytes.
    # Therefore, we set '!color_mark' to '03 00 00 00' only if the item's flag is C3,
    # and add the corresponding color properties.
    # For C0, C1, C2 items, we set '!color_mark' to a non-matching value ('00 00 00 00')
    # and do NOT include the additional color properties in `formatted_data`, as the parser
    # will not attempt to read them for these cases.
    if color_flag == C3:
        formatted_data["!color_mark"] = "03 00 00 00"
        formatted_data.update(
            {
                "main_color": _random_color_str(),
                "main_shine": _random_color_str(),
                "main_strength": random.randint(
                    0, 100
                ),  # _parse_and_pack_float uses default scale=100
                "main_texture": random.randint(
                    0, 100
                ),  # _parse_and_pack_float uses default scale=100
                "sub_color": _random_color_str(),
                "sub_shine": _random_color_str(),
                "sub_strength": random.randint(0, 100),
                "sub_texture": random.randint(0, 100),
            }
        )
    else:
        # For items with C0, C1, or C2 flags, the binary data does not contain
        # the conditional color/shine properties. The parser checks for '03 00 00 00'.
        # Any other value for !color_mark will cause the parser to skip these fields.
        formatted_data["!color_mark"] = (
            "00 00 00 00"  # Dummy value indicating no extra color data
        )

    return formatted_data


@pytest.mark.parametrize(
    "_", range(300)
)  # Reduced iterations for faster testing; consider 300+ for thoroughness
def test_random_accessory_roundtrip(_):
    original_accessories_data = {}

    # --- Construct random original data for all 10 accessory slots ---
    for i in range(1, 11):  # Loop for accessory_01 through accessory_10
        # Generate data for each individual accessory slot
        item_data = format_accessory_for_test()
        original_accessories_data[f"accessory_{i:02}"] = item_data

    # --- Serialize and then parse back the data ---
    stream = BytesIO()
    # Pass debug_mode=True to see detailed serialization logs
    serialize_accessories_data(original_accessories_data, stream, debug_mode=False)
    stream.seek(0)  # Reset stream position to the beginning for parsing
    # Pass debug_mode=True to see detailed parsing logs
    parsed_accessories_data = parse_accessories_data(stream, debug_mode=False)

    # --- Compare the original and parsed data ---
    print(f"\n--- Accessory Roundtrip Test {_+1} ---")

    # Optional: Print key data points for debugging discrepancies
    for i in range(1, 11):
        slot_key = f"accessory_{i:02}"
        orig_item = original_accessories_data.get(slot_key, {})
        parsed_item = parsed_accessories_data.get(slot_key, {})

        print(f"  Slot: {slot_key}")
        # Use localized names from game_data for better readability in debug output
        orig_type_name = (
            ACCESSORY_TYPE[0]["name"]["zh"]
            if orig_item.get("type") == -1
            else (
                next(
                    (
                        t["name"]["zh"]
                        for t in ACCESSORY_TYPE
                        if t["id"] == orig_item.get("type")
                    ),
                    "Unknown Type",
                )
            )
        )
        parsed_type_name = (
            ACCESSORY_TYPE[0]["name"]["zh"]
            if parsed_item.get("type") == -1
            else (
                next(
                    (
                        t["name"]["zh"]
                        for t in ACCESSORY_TYPE
                        if t["id"] == parsed_item.get("type")
                    ),
                    "Unknown Type",
                )
            )
        )

        print(
            f"    Original Type: {orig_type_name} ({orig_item.get('type')}), ID: {orig_item.get('id')}, Slot: {orig_item.get('slot')}"
        )
        print(
            f"    Parsed Type: {parsed_type_name} ({parsed_item.get('type')}), ID: {parsed_item.get('id')}, Slot: {parsed_item.get('slot')}"
        )

        if orig_item.get("!color_mark") == "03 00 00 00":
            print(f"    Original Main Color: {orig_item.get('main_color')}")
            print(f"    Parsed Main Color: {parsed_item.get('main_color')}")
            print(f"    Original Sub Color: {orig_item.get('sub_color')}")
            print(f"    Parsed Sub Color: {parsed_item.get('sub_color')}")

    # Filter the parsed data to remove keys added by the parser (e.g., '#info')
    # and ensure only the serialized/deserialized fields are compared.
    filtered_parsed_accessories_data = {}
    for slot_key, original_item in original_accessories_data.items():
        parsed_item = parsed_accessories_data.get(slot_key, {})
        filtered_item = {}
        for key, value in original_item.items():
            # Explicitly include '!color_mark' as it is serialized and deserialized
            if key == "!color_mark":
                filtered_item[key] = parsed_item.get(key)
            # Exclude keys starting with '#' as they are typically parser-added metadata
            elif not key.startswith("#"):
                # For nested dictionaries (position, rotation, scale), copy them directly.
                # Assuming `compare_dicts` handles nested dictionary comparison recursively.
                if key in ["position", "rotation", "scale"]:
                    filtered_item[key] = parsed_item.get(key)
                else:
                    filtered_item[key] = parsed_item.get(key)

        # If the original item expected conditional color properties, copy them to filtered_item
        # This is crucial because if `original_item['!color_mark'] != '03 00 00 00'`,
        # these keys won't exist in `original_item` for the loop above.
        # But if `original_item['!color_mark'] == '03 00 00 00'`, we need to ensure they are copied for comparison.
        if original_item.get("!color_mark") == "03 00 00 00":
            color_properties = [
                "main_color",
                "main_shine",
                "main_strength",
                "main_texture",
                "sub_color",
                "sub_shine",
                "sub_strength",
                "sub_texture",
            ]
            for prop_key in color_properties:
                if (
                    prop_key in original_item
                ):  # Only copy if it was present in the original data
                    filtered_item[prop_key] = parsed_item.get(prop_key)

        filtered_parsed_accessories_data[slot_key] = filtered_item

    # Perform the comparison using the (filtered) parsed data and original data.
    # The `compare_dicts` function should handle float precision.
    compare_dicts(original_accessories_data, filtered_parsed_accessories_data)

    print(f"--- Accessory Roundtrip Test {_+1} Passed! ---")
