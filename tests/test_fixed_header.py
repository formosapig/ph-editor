import pytest
from io import BytesIO
from parsers.fixed_header_parser import parse_fixed_header
from serializers.fixed_header_serializer import serialize_fixed_header

def test_fixed_header_roundtrip():
    original = {
        "mark": "PlayHome_Female",
        "strange": "AACD",  # UTF-8 字元
        "version": 3
    }

    stream = BytesIO()
    serialize_fixed_header(original, stream)
    stream.seek(0)
    parsed = parse_fixed_header(stream)

    assert parsed['mark'].strip('\x00') == original['mark']
    assert parsed['strange'].strip('\x00') == original['strange']
    assert parsed['version'] == original['version']
