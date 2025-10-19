"""Password hashing module with custom algorithm implementation.

This module provides a pure Python implementation of password hashing functions
for reference and testing purposes. The C++ implementation in encryption_backend
is the production version for performance.
"""

import secrets
import string
import re


def generate_salt(length=16):
    """Generate a random salt string.
    
    Args:
        length: Length of salt string (default: 16)
    
    Returns:
        Random salt string with first char being ASCII letter, rest printable chars
    """
    first_char = secrets.choice(string.ascii_letters)
    remaining_chars = ''.join(chr(secrets.randbelow(126 - 37) + 37) for _ in range(length - 1))
    return first_char + remaining_chars


def _sort_by_nth_element(arr, n):
    """Sort array by removing every nth element cyclically.
    
    Internal helper for hash algorithm.
    """
    arr_copy = list(arr)
    result = bytearray()
    length = len(arr_copy)
    index = 0

    for _ in range(length):
        index = (index + n - 1) % len(arr_copy)
        result.append(arr_copy[index])
        del arr_copy[index]

    return result


def _internal_hash_password(password, salt=None, memo=None):
    """Custom hash function that combines salt and password.
    
    Internal implementation of core hash algorithm.
    """
    if salt is None:
        salt = generate_salt()
    combined = salt + "$" + password
    combined_bytes = combined.encode('utf-8')
    
    hash1 = ''
    hash4 = None
    accumulator = combined_bytes[0]
    memo_length = len(memo) if memo else 0
    
    if memo is not None and memo_length > 0:
        hash4 = memo[memo_length - 1]
        index = combined_bytes[-2] * 97
        index = index % memo_length
        string_memo = memo[index]
        string_memo_length = len(string_memo)
        index = combined_bytes[-7] * 113
        index = index % string_memo_length
        accumulator = string_memo[index].encode('utf-8')[0]
    else:
        index = combined_bytes[0] % 90
        accumulator = index + 37
        
    if accumulator > 96:
        accumulator -= 70
    else:
        accumulator -= 64
    
    # Generate hash1
    for i in range(len(combined)):
        hash_value = accumulator * 113
        hash_value += combined_bytes[i]
        accumulator += 2
        
        if accumulator > 48:
            accumulator -= 23

        hash1 += chr(((hash_value % 90)) & (((hash_value // 90)) % 90 + 37))

    hash1_bytes = hash1.encode('utf-8')
    sorted_hash_bytes = _sort_by_nth_element(hash1_bytes, accumulator % 5)
    
    # Generate hash2
    hash2 = ''
    hash_value = 0
    
    for byte_val in sorted_hash_bytes:
        hash_value *= 71
        hash_value += byte_val
        
        while hash_value > 128:
            hash2 += chr((hash_value % 90) + 37)
            hash_value = hash_value // 90
    
    hash2 += chr((hash_value % 90) + 37)
    
    # Generate hash3
    hash3 = ''
    for byte_val in sorted_hash_bytes:
        hash_value *= 997
        hash_value += byte_val
        
        while hash_value > 128:
            hash3 += chr((hash_value % 90) + 37)
            hash_value = hash_value // 90
    
    hash3 += chr((hash_value % 90) + 37)
    
    # Generate hash4
    if hash4:
        hash_4_bytes = hash4.encode('utf-8')
    else:
        hash_4_bytes = sorted_hash_bytes
        hash4 = ''
        
    multiplier = 1997 if memo_length > 73 else 23
    
    for byte_val in hash_4_bytes:
        hash_value *= multiplier
        hash_value += byte_val
        
        while hash_value > 128:
            hash4 += chr((hash_value % 90) + 37)
            hash_value = hash_value // 90
    
    if memo_length > 47:
        return (f"${salt}$/${hash2}", hash1, hash2, hash3, hash4, hash3)
    else:
        return (f"${salt}$/${hash2}${hash4}", hash1, hash2, hash3, hash3, hash4)


def check_password_strength(password):
    """Check password strength based on various criteria (0-5 scale).
    
    Args:
        password: Password string to check
        
    Returns:
        Strength score from 0-5
    """
    strength = 0
    
    if len(password) >= 8:
        strength += 1
    if re.search(r'[a-z]', password):
        strength += 1
    if re.search(r'[A-Z]', password):
        strength += 1
    if re.search(r'[0-9]', password):
        strength += 1
    if re.search(r'[^a-zA-Z0-9]', password):
        strength += 1
    
    return strength


def hash_password(password, cost=2, salt=None):
    """Hash a password using custom iterative algorithm.
    
    Args:
        password: Password string to hash
        cost: Iteration cost factor (iterations = 2^cost), default 2
        salt: Optional salt string, generates random if not provided
        
    Returns:
        Final hashed password string
    """
    memo = {}
    iterations = pow(2, cost)
    
    for i in range(iterations):
        password_tuple = _internal_hash_password(password, salt, memo)
        
        # Store results in memo for next iteration
        memo[16*i] = password_tuple[0]
        memo[16*i + 1] = password_tuple[1]
        memo[16*i + 2] = password_tuple[2]
        memo[16*i + 3] = password_tuple[3]
        memo[16*i + 4] = password_tuple[4]
        memo[16*i + 15] = password_tuple[5]
        memo[16*i + 6] = password_tuple[5] + password_tuple[2]
        memo[16*i + 7] = password_tuple[5] + password_tuple[3]
        memo[16*i + 8] = password_tuple[5] + password_tuple[4]
        memo[16*i + 9] = password_tuple[5] + password_tuple[1]
        memo[16*i + 10] = password_tuple[5] + password_tuple[0]
        memo[16*i + 11] = password_tuple[5] + password_tuple[2]
        memo[16*i + 12] = password_tuple[2] + password_tuple[3]
        memo[16*i + 13] = password_tuple[2] + password_tuple[4]
        memo[16*i + 14] = password_tuple[0] + password_tuple[1]
        memo[16*i + 5] = password_tuple[0] + password_tuple[3]
        
        password = password_tuple[0]
    
    return password
