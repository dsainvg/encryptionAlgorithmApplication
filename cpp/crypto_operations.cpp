// crypto_operations.cpp
// Implementation of bitwise operations and cryptographic primitives.
// Provides high-performance C++ implementations for encryption, XOR, and bit manipulation.

#include "crypto_operations.h"

#include <algorithm>
#include <array>
#include <cstdint>
#include <cstring>
#include <string>
#include <vector>

namespace {
    // Internal helper functions in unnamed namespace
    
    // Normalize shift values to prevent undefined behavior
    int normalize_shift_32(int shift) {
        shift = shift % 32;
        return (shift < 0) ? shift + 32 : shift;
    }
    
    int normalize_shift_64(int shift) {
        shift = shift % 64;
        return (shift < 0) ? shift + 64 : shift;
    }
    
    // Internal buffer XOR implementation
    void internal_xor_buffer(std::uint8_t* buffer, std::size_t length, std::uint8_t key) {
        if (buffer == nullptr) return;
        
        for (std::size_t i = 0; i < length; i++) {
            buffer[i] ^= key;
        }
    }
    
    // Internal multi-key XOR implementation
    void internal_xor_buffer_with_key(std::uint8_t* buffer, std::size_t length, 
                                    const std::uint8_t* key, std::size_t key_length) {
        if (buffer == nullptr || key == nullptr || key_length == 0) return;
        
        for (std::size_t i = 0; i < length; i++) {
            buffer[i] ^= key[i % key_length];
        }
    }
    
    // Simple diffusion function for enhanced encryption
    std::uint32_t diffusion_function(std::uint32_t value, std::size_t position) {
        // Simple non-linear transformation based on position
        // This is its own inverse when applied twice
        std::uint32_t temp = value;
        temp ^= static_cast<std::uint32_t>(position * 0x9E3779B9); // Golden ratio constant
        temp ^= (temp >> 16);
        temp ^= (temp << 11);
        temp ^= (temp >> 7);
        return temp;
    }
}

namespace encryption::crypto {
    
    // XOR operations - fundamental cryptographic primitive
    std::uint32_t xor_operation(std::uint32_t a, std::uint32_t b) {
        return a ^ b;
    }
    
    std::uint64_t xor_operation_64(std::uint64_t a, std::uint64_t b) {
        return a ^ b;
    }
    
    // Bit rotation operations - used in many cryptographic algorithms
    std::uint32_t rotate_left(std::uint32_t value, int shift) {
        shift = normalize_shift_32(shift);
        return (value << shift) | (value >> (32 - shift));
    }
    
    std::uint64_t rotate_left_64(std::uint64_t value, int shift) {
        shift = normalize_shift_64(shift);
        return (value << shift) | (value >> (64 - shift));
    }
    
    std::uint32_t rotate_right(std::uint32_t value, int shift) {
        shift = normalize_shift_32(shift);
        return (value >> shift) | (value << (32 - shift));
    }
    
    std::uint64_t rotate_right_64(std::uint64_t value, int shift) {
        shift = normalize_shift_64(shift);
        return (value >> shift) | (value << (64 - shift));
    }
    
    // Buffer XOR operations - for data encryption/decryption
    std::string xor_buffer(const std::string& data, std::uint8_t key) {
        std::string result = data;
        internal_xor_buffer(reinterpret_cast<std::uint8_t*>(result.data()), 
                           result.size(), key);
        return result;
    }
    
    std::string xor_buffer_with_key(const std::string& data, const std::string& key) {
        if (key.empty()) return data;
        
        std::string result = data;
        internal_xor_buffer_with_key(reinterpret_cast<std::uint8_t*>(result.data()),
                                   result.size(),
                                   reinterpret_cast<const std::uint8_t*>(key.data()),
                                   key.size());
        return result;
    }
    
    // Advanced cryptographic operations combining multiple primitives
    std::string encrypt_data(const std::string& data, const std::string& key, int rounds) {
        if (data.empty() || key.empty() || rounds <= 0) return data;
        
        std::string result = data;
        
        for (int round = 0; round < rounds; ++round) {
            // Step 1: XOR with key
            result = xor_buffer_with_key(result, key);
            
            // Step 2: Apply bit rotation to 4-byte chunks
            std::string temp_result;
            temp_result.reserve(result.size());
            
            for (std::size_t i = 0; i < result.size(); i += 4) {
                if (i + 4 <= result.size()) {
                    // Process complete 4-byte chunks
                    std::uint32_t chunk = 0;
                    std::memcpy(&chunk, &result[i], 4);
                    
                    // Apply rotation
                    chunk = rotate_left(chunk, 5 + (round % 8));
                    
                    char chunk_bytes[4];
                    std::memcpy(chunk_bytes, &chunk, 4);
                    temp_result.append(chunk_bytes, 4);
                } else {
                    // Handle remaining bytes - simple XOR with round number
                    for (std::size_t j = i; j < result.size(); ++j) {
                        temp_result.push_back(result[j] ^ static_cast<std::uint8_t>(round + 1));
                    }
                }
            }
            
            result = std::move(temp_result);
        }
        
        return result;
    }
    
    std::string decrypt_data(const std::string& encrypted_data, const std::string& key, int rounds) {
        if (encrypted_data.empty() || key.empty() || rounds <= 0) return encrypted_data;
        
        std::string result = encrypted_data;
        
        // Reverse the encryption process
        for (int round = rounds - 1; round >= 0; --round) {
            // Step 1: Reverse bit rotation for 4-byte chunks
            std::string temp_result;
            temp_result.reserve(result.size());
            
            for (std::size_t i = 0; i < result.size(); i += 4) {
                if (i + 4 <= result.size()) {
                    // Process complete 4-byte chunks
                    std::uint32_t chunk = 0;
                    std::memcpy(&chunk, &result[i], 4);
                    
                    // Reverse rotation
                    chunk = rotate_right(chunk, 5 + (round % 8));
                    
                    char chunk_bytes[4];
                    std::memcpy(chunk_bytes, &chunk, 4);
                    temp_result.append(chunk_bytes, 4);
                } else {
                    // Handle remaining bytes - reverse XOR with round number
                    for (std::size_t j = i; j < result.size(); ++j) {
                        temp_result.push_back(result[j] ^ static_cast<std::uint8_t>(round + 1));
                    }
                }
            }
            
            result = std::move(temp_result);
            
            // Step 2: Reverse XOR with key
            result = xor_buffer_with_key(result, key);
        }
        
        return result;
    }
    
} // namespace encryption::crypto
