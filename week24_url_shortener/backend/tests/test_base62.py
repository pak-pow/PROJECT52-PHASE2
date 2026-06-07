import pytest #type: ignore
from app.utils.base62 import encode, decode 

def test_encode_basic_numbers():
    """Test that standard numbers encode correctly"""
    assert encode(1) == 'b'
    assert encode(61) == '9'
    assert encode(62) == 'ba'

def test_encode_zero_or_negative():
    """The encoder should reject 0 or negative numbers since db IDs start at 1"""
    with pytest.raises(ValueError):
        encode(0)
        
    with pytest.raises(ValueError):
        encode(-5)