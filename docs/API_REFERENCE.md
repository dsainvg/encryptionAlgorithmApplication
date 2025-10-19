# Encryption Backend - Quick API Reference

## Module Import
```python
import encryption_backend as backend
```

## Password Hashing Functions

### `generate_salt(bytes=16) -> str`
Generate a cryptographically secure random salt.

**Parameters:**
- `bytes` (int, optional): Length of salt string. Default: 16

**Returns:** String containing random salt

**Example:**
```python
salt = backend.generate_salt(16)
print(f"Generated salt: {salt}")
```

---

### `hash_password(password, cost=2, salt=None) -> str`
Hash a password using custom iterative algorithm.

**Parameters:**
- `password` (str): Password string to hash
- `cost` (int, optional): Iteration cost (iterations = 2^cost). Default: 2
- `salt` (str, optional): Salt string. If None, generates random salt

**Returns:** Final hashed password string

**Example:**
```python
# With auto-generated salt
hashed = backend.hash_password("MySecretPassword123!", cost=12)

# With custom salt
salt = backend.generate_salt()
hashed = backend.hash_password("MySecretPassword123!", cost=12, salt=salt)
```

**Performance Guide:**
| Cost | Iterations | Approx Time | Use Case |
|------|-----------|-------------|----------|
| 2    | 4         | ~1ms        | Testing only |
| 8    | 256       | ~30ms       | Low security |
| 12   | 4096      | ~250ms      | Recommended |
| 15   | 32768     | ~2s         | High security |
| 18   | 262144    | ~16s        | Maximum security |

---

### `check_password_strength(password) -> bool`
Validate password meets security requirements.

**Parameters:**
- `password` (str): Password to validate

**Returns:** True if password meets all requirements, False otherwise

**Requirements:**
- Minimum 8 characters
- At least one lowercase letter
- At least one uppercase letter
- At least one digit
- At least one special character
- No whitespace characters

**Example:**
```python
password = "Secret123!@#"
if backend.check_password_strength(password):
    print("✓ Password is strong")
else:
    print("✗ Password is weak")
```

---

## Data Encryption Functions

### `encrypt_data(data, key, rounds=1) -> bytes`
Encrypt binary data using XOR and bit rotation.

**Parameters:**
- `data` (bytes): Binary data to encrypt
- `key` (bytes): Encryption key (typically hashed password)
- `rounds` (int, optional): Number of encryption rounds. Default: 1

**Returns:** Encrypted binary data

**Example:**
```python
# Encrypt file data
password = "MyPassword123!"
key = backend.hash_password(password, cost=12).encode('utf-8')

with open("document.txt", "rb") as f:
    plaintext = f.read()

encrypted = backend.encrypt_data(plaintext, key, rounds=3)

with open("document.txt.encrypted", "wb") as f:
    f.write(encrypted)
```

---

### `decrypt_data(encrypted_data, key, rounds=1) -> bytes`
Decrypt binary data encrypted with `encrypt_data()`.

**Parameters:**
- `encrypted_data` (bytes): Encrypted binary data
- `key` (bytes): Decryption key (must match encryption key)
- `rounds` (int): Number of rounds (must match encryption rounds)

**Returns:** Decrypted binary data

**Example:**
```python
# Decrypt file data
password = "MyPassword123!"
key = backend.hash_password(password, cost=12).encode('utf-8')

with open("document.txt.encrypted", "rb") as f:
    encrypted = f.read()

decrypted = backend.decrypt_data(encrypted, key, rounds=3)

with open("document.txt.decrypted", "wb") as f:
    f.write(decrypted)
```

---

## Complete Example: File Encryption

```python
import encryption_backend as backend
import os

def encrypt_file(filepath, password, cost=12, rounds=3):
    """Encrypt a file with password protection."""
    
    # Generate salt and hash password
    salt = backend.generate_salt(16)
    key = backend.hash_password(password, cost=cost, salt=salt).encode('utf-8')
    
    # Read and encrypt file
    with open(filepath, "rb") as f:
        plaintext = f.read()
    
    encrypted = backend.encrypt_data(plaintext, key, rounds=rounds)
    
    # Save encrypted file and metadata
    output_file = filepath + ".encrypted"
    with open(output_file, "wb") as f:
        f.write(encrypted)
    
    # Save salt and cost for decryption
    metadata_file = filepath + ".metadata"
    with open(metadata_file, "w") as f:
        f.write(f"salt={salt}\n")
        f.write(f"cost={cost}\n")
        f.write(f"rounds={rounds}\n")
    
    return output_file, metadata_file


def decrypt_file(encrypted_filepath, metadata_filepath, password):
    """Decrypt a file with password."""
    
    # Load metadata
    with open(metadata_filepath, "r") as f:
        lines = f.readlines()
        salt = lines[0].split("=")[1].strip()
        cost = int(lines[1].split("=")[1].strip())
        rounds = int(lines[2].split("=")[1].strip())
    
    # Hash password with saved salt
    key = backend.hash_password(password, cost=cost, salt=salt).encode('utf-8')
    
    # Read and decrypt file
    with open(encrypted_filepath, "rb") as f:
        encrypted = f.read()
    
    decrypted = backend.decrypt_data(encrypted, key, rounds=rounds)
    
    # Save decrypted file
    output_file = encrypted_filepath.replace(".encrypted", ".decrypted")
    with open(output_file, "wb") as f:
        f.write(decrypted)
    
    return output_file


# Usage example
if __name__ == "__main__":
    # Check password strength
    password = "MySecurePassword123!@#"
    if not backend.check_password_strength(password):
        print("Warning: Weak password!")
        exit(1)
    
    # Encrypt file
    print("Encrypting file...")
    encrypted_file, metadata_file = encrypt_file(
        "important_document.pdf",
        password,
        cost=12,
        rounds=3
    )
    print(f"✓ Encrypted: {encrypted_file}")
    print(f"✓ Metadata: {metadata_file}")
    
    # Decrypt file
    print("\nDecrypting file...")
    decrypted_file = decrypt_file(
        encrypted_file,
        metadata_file,
        password
    )
    print(f"✓ Decrypted: {decrypted_file}")
```

---

## Performance Tips

### 1. **Choose Appropriate Cost**
- Higher cost = more secure but slower
- Recommended: cost=12 for general use (250ms per hash)
- For high-security: cost=15 (2 seconds per hash)

### 2. **Use Multiple Rounds for Large Files**
```python
# For files < 1 MB: rounds=1 is sufficient
# For files > 1 MB: rounds=3-5 for better security
```

### 3. **Memory-Mapped Files for Large Data**
```python
import mmap

with open("large_file.bin", "rb") as f:
    with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mmapped:
        # Process in chunks
        CHUNK_SIZE = 1024 * 1024  # 1 MB
        for i in range(0, len(mmapped), CHUNK_SIZE):
            chunk = mmapped[i:i+CHUNK_SIZE]
            encrypted_chunk = backend.encrypt_data(chunk, key)
            # ... process chunk
```

---

## Error Handling

```python
import encryption_backend as backend

try:
    # Validate password strength first
    password = input("Enter password: ")
    if not backend.check_password_strength(password):
        raise ValueError("Password does not meet security requirements")
    
    # Hash password
    hashed = backend.hash_password(password, cost=12)
    
    # Encrypt data
    data = b"Secret information"
    encrypted = backend.encrypt_data(data, hashed.encode('utf-8'))
    
except ValueError as e:
    print(f"Validation error: {e}")
except Exception as e:
    print(f"Encryption error: {e}")
```

---

## Security Best Practices

1. **Never store passwords in plaintext** - Always use `hash_password()`
2. **Use high cost values** - Minimum cost=12 for production
3. **Generate unique salts** - Use `generate_salt()` for each password
4. **Store salts safely** - Save salts with encrypted data (they're not secret)
5. **Validate passwords** - Use `check_password_strength()` before hashing
6. **Use multiple rounds** - For sensitive data, use rounds=3 or higher
7. **Secure key derivation** - Derive encryption keys from hashed passwords

---

## Module Information

**Module Name:** `encryption_backend`  
**Language:** C++ (Python bindings via pybind11)  
**Platform:** Windows (64-bit)  
**Python Version:** 3.14+ (rebuild required for other versions)  
**License:** [Your License Here]

**Author:** [Your Name]  
**Version:** 2.0.0 (Refactored)  
**Last Updated:** October 19, 2025
