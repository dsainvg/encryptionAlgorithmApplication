// crypto_operations.h
// Public API for cryptographic operations exposed to Python.
// Provides XOR, bit rotation, and data encryption/decryption functions.

#pragma once
#include <cstdint>
#include <cstddef>
#include <string>
#include <vector>

namespace encryption::crypto {

// Advanced cryptographic operations
// Combines multiple primitives for more complex encryption schemes
std::string encrypt_data(const std::string& data, const std::string& key, int rounds = 1);
std::string decrypt_data(const std::string& encrypted_data, const std::string& key, int rounds = 1);

} // namespace encryption::crypto
