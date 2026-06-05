# =============================================================================
# base62.py — The Mathematical Hashing Engine
#
# WHY BASE62?
#   - MD5/SHA256 produce strings that are far too long and can collide.
#   - Base62 maps a unique integer database ID to a short, URL-safe string.
#   - 6 characters = 62^6 = ~56 billion unique combinations. More than enough.
#
# HOW IT WORKS:
#   Just like how Base10 uses digits 0-9 and Base16 (hex) uses 0-9 + A-F,
#   Base62 uses a-z + A-Z + 0-9 (62 characters total).
#   We repeatedly divide the integer by 62 and map each remainder to a character.
#
#   Example: encode(10000) -> "2Bi"
# =============================================================================

ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
BASE = len(ALPHABET)  # 62


def encode(num: int) -> str:
    """
    Converts a positive integer (database ID) into a Base62 short code.

    Args:
        num: A positive integer, typically a database auto-increment ID.

    Returns:
        A short URL-safe alphanumeric string.

    Example:
        >>> encode(1)      # 'a'
        >>> encode(61)     # '9'
        >>> encode(62)     # 'ba'
        >>> encode(10000)  # '2Bi'
    """
    if num <= 0:
        raise ValueError(f"encode() requires a positive integer, got: {num}")

    chars = []
    while num > 0:
        chars.append(ALPHABET[num % BASE])
        num //= BASE

    # Characters are built in reverse order (LSB first), so reverse before joining
    return ''.join(reversed(chars))


def decode(short_code: str) -> int:
    """
    Converts a Base62 short code back into the original integer ID.
    Useful for debugging and verification.

    Args:
        short_code: A Base62 encoded string.

    Returns:
        The original integer ID.

    Example:
        >>> decode('2Bi')  # 10000
    """
    num = 0
    for char in short_code:
        if char not in ALPHABET:
            raise ValueError(f"Invalid Base62 character: '{char}'")
        num = num * BASE + ALPHABET.index(char)
    return num
