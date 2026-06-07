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
        
def test_encode_decode_symmetry():
    """The golden rule: is that decoding an encoded string must return the original number"""
    test_number = [1,42,100, 9999,123456789]
    
    for num in test_number:
        encoded_str = encode(num)
        decoded_num = decode(encoded_str)
        
        assert decoded_num == num, f"Failed on {num}. Got {decoded_num} instead"
        
def test_decode_invalid_string():
    """Decoding a string with invalid characters (like symbols) should fail"""
    with pytest.raises(ValueError):
        decode("2B@i!")