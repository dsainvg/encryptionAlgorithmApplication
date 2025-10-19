// password_hasher.cpp
// Implementation of password hashing and verification helpers.

#include "password_hasher.h"

#include <algorithm>
#include <array>
#include <cctype>
#include <chrono>
#include <cstdint>
#include <random>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>

namespace {
    using Byte = std::uint8_t;

    // Helper: sort bytes by nth element cyclically
    std::vector<Byte> sort_by_nth_element(const std::vector<Byte>& data, std::size_t n) {
        if (data.empty()) return {};
        std::vector<Byte> arr_copy = data;
        std::vector<Byte> result;
        std::size_t index = 0;
        for (std::size_t i = 0; i < data.size(); ++i) {
            // Perform modulo in signed space to match Python's modulo semantics
            long long idx = static_cast<long long>(index) + static_cast<long long>(n) - 1;
            long long mod = idx % static_cast<long long>(arr_copy.size());
            if (mod < 0) mod += static_cast<long long>(arr_copy.size());
            index = static_cast<std::size_t>(mod);
            result.push_back(arr_copy[index]);
            arr_copy.erase(arr_copy.begin() + index);
        }
        return result;
    }


    // Encode a string's bytes as if each char is a Latin-1 codepoint, then to UTF-8 bytes
    std::vector<Byte> latin1_to_utf8_bytes(const std::string& s) {
        std::vector<Byte> out;
        out.reserve(s.size());
        for (unsigned char uc : s) {
            if (uc < 0x80) {
                out.push_back(static_cast<Byte>(uc));
            } else if (uc < 0xC0) { // 0x80..0xBF -> C2 80..BF
                out.push_back(static_cast<Byte>(0xC2));
                out.push_back(static_cast<Byte>(uc));
            } else { // 0xC0..0xFF -> C3 80..BF
                out.push_back(static_cast<Byte>(0xC3));
                out.push_back(static_cast<Byte>(uc - 0x40));
            }
        }
        return out;
    }

    // Custom hash function (C++ version of _hash_password)
    std::tuple<std::string, std::string, std::string, std::string, std::string, std::string>
    internal_hash_password(const std::string& password, const std::string* salt_ptr = nullptr, const std::vector<std::string>* memo = nullptr) {
        std::string salt = salt_ptr ? *salt_ptr : "";
        std::string combined = salt + "$" + password;
        std::vector<Byte> combined_bytes(combined.begin(), combined.end());

        std::string hash1, hash2, hash3, hash4;
        int accumulator = static_cast<int>(combined_bytes[0]);
        std::size_t memo_length = memo ? memo->size() : 0;
        const std::string* string_memo = nullptr;
        
        if (memo && memo_length > 0) {
            hash4 = (*memo)[memo_length - 1];
            int index = static_cast<int>(combined_bytes[combined_bytes.size() - 2]) * 97;
            index = index % static_cast<int>(memo_length);
            string_memo = &(*memo)[index];
            std::size_t string_memo_length = string_memo->size();
            index = static_cast<int>(combined_bytes[combined_bytes.size() - 7]) * 113;
            index = index % static_cast<int>(string_memo_length);
            // Take the first byte of the character's UTF-8 encoding (ASCII => itself)
            accumulator = static_cast<unsigned char>((*string_memo)[index]);
        } else {
            int index = static_cast<int>(combined_bytes[0]) % 90;
            accumulator = static_cast<Byte>(index + 37);
        }

        if (accumulator > 96)
            accumulator -= 70;
        else
            accumulator -= 64;

        // Generate hash1
        for (std::size_t i = 0; i < combined.size(); ++i) {
            int hash_value = accumulator * 113;
            hash_value += combined_bytes[i];
            accumulator += 2;
            
            if (accumulator > 48)
                accumulator -= 23;

            char c = static_cast<char>(((hash_value % 90)) & (((hash_value / 90) % 90) + 37));
            hash1 += c;
        }
        
        // Sort hash1 bytes using custom algorithm
        std::vector<Byte> hash1_bytes = latin1_to_utf8_bytes(hash1);
        int sort_index = accumulator % 5;
        std::vector<Byte> sorted_hash_bytes = sort_by_nth_element(hash1_bytes, static_cast<std::size_t>(sort_index));

        // Generate hash2
        int hash_value = 0;
        for (Byte byte_val : sorted_hash_bytes) {
            hash_value *= 71;
            hash_value += byte_val;
            
            while (hash_value > 128) {
                hash2 += static_cast<char>((hash_value % 90) + 37);
                hash_value = hash_value / 90;
            }
        }
        hash2 += static_cast<char>((hash_value % 90) + 37);

        // Generate hash3 (carry over hash_value from hash2)
        for (Byte byte_val : sorted_hash_bytes) {
            hash_value *= 997;
            hash_value += byte_val;
            
            while (hash_value > 128) {
                hash3 += static_cast<char>((hash_value % 90) + 37);
                hash_value = hash_value / 90;
            }
        }
        hash3 += static_cast<char>((hash_value % 90) + 37);

        // Generate hash4
        std::vector<Byte> hash_4_bytes;
        if (!hash4.empty()) {
            hash_4_bytes.assign(hash4.begin(), hash4.end());
        } else {
            hash_4_bytes = sorted_hash_bytes;
            hash4.clear();
        }
        
        int multiplier = (memo_length > 73) ? 1997 : 23;
        for (Byte byte_val : hash_4_bytes) {
            hash_value *= multiplier;
            hash_value += byte_val;
            
            while (hash_value > 128) {
                hash4 += static_cast<char>((hash_value % 90) + 37);
                hash_value = hash_value / 90;
            }
        }
        
        if (memo_length > 47) {
            return { "$" + salt + "$/$" + hash2, hash1, hash2, hash3, hash4, hash3 };
        } else {
            return { "$" + salt + "$/$" + hash2 + "$" + hash4, hash1, hash2, hash3, hash3, hash4 };
        }
    }
}

namespace encryption::password {
    std::string generate_salt(std::size_t bytes) {
        std::random_device rd;
        std::mt19937_64 gen(
            (static_cast<std::uint64_t>(rd()) << 32) ^
            static_cast<std::uint64_t>(
                std::chrono::high_resolution_clock::now().time_since_epoch().count()));
        std::uniform_int_distribution<int> dist(0, 255);

        static const char ascii_letters[] =
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
        std::string salt(bytes, '\0');
        std::uniform_int_distribution<int> ascii_letter_dist(0, sizeof(ascii_letters) - 2); // exclude null terminator
        std::uniform_int_distribution<int> printable_dist(37, 125); // 126 not included

        // First character: random ascii letter
        salt[0] = ascii_letters[ascii_letter_dist(gen)];
        // Remaining characters: random printable (ASCII 37..125)
        for (std::size_t i = 1; i < bytes; ++i) {
            salt[i] = static_cast<char>(printable_dist(gen));
        }
        return salt;
    }

    std::string hash_password(const std::string& password, int cost, std::optional<std::string> salt) {
        std::vector<std::string> memo;
        std::vector<std::string> password_tuple;
        std::string current_password = password;

        int iterations = 1 << cost;
        for (int i = 0; i < iterations; ++i) {
            password_tuple.clear();
            // Generate a new salt each iteration when not provided, matching Python behavior
            std::string local_salt = salt ? *salt : generate_salt();
            auto hash_result = internal_hash_password(current_password, &local_salt, &memo);
            password_tuple.push_back(std::get<0>(hash_result));
            password_tuple.push_back(std::get<1>(hash_result));
            password_tuple.push_back(std::get<2>(hash_result));
            password_tuple.push_back(std::get<3>(hash_result));
            password_tuple.push_back(std::get<4>(hash_result));
            password_tuple.push_back(std::get<5>(hash_result));

            // Memoization logic (mimics the Python dict with vector)
            if (memo.size() < (16 * (i + 1))) memo.resize(16 * (i + 1));
            memo[16 * i + 0] = password_tuple[0];
            memo[16 * i + 1] = password_tuple[1];
            memo[16 * i + 2] = password_tuple[2];
            memo[16 * i + 3] = password_tuple[3];
            memo[16 * i + 4] = password_tuple[4];
            memo[16 * i + 15] = password_tuple[5];
            memo[16 * i + 6] = password_tuple[5] + password_tuple[2];
            memo[16 * i + 7] = password_tuple[5] + password_tuple[3];
            memo[16 * i + 8] = password_tuple[5] + password_tuple[4];
            memo[16 * i + 9] = password_tuple[5] + password_tuple[1];
            memo[16 * i + 10] = password_tuple[5] + password_tuple[0];
            memo[16 * i + 11] = password_tuple[5] + password_tuple[2];
            memo[16 * i + 12] = password_tuple[2] + password_tuple[3];
            memo[16 * i + 13] = password_tuple[2] + password_tuple[4];
            memo[16 * i + 14] = password_tuple[0] + password_tuple[1];
            memo[16 * i + 5] = password_tuple[0] + password_tuple[3];

            current_password = password_tuple[0];
        }
        return current_password;
    }

    bool check_password_strength(const std::string& password) {
        if(password.size() < 8) {
            return false; // Password must be at least 8 characters long
        }
        if(password.find_first_of(" \t\n\r") != std::string::npos) {
            return false; // Password must not contain whitespace
        }
        if(password.find_first_of("0123456789") == std::string::npos) {
            return false; // Password must contain at least one digit
        }
        if(password.find_first_of("!@#$%^&*()_+-={}|[]\\:\";'<>?,./`~") == std::string::npos) {
            return false; // Password must contain at least one special character
        }
        if(password.find_first_of("abcdefghijklmnopqrstuvwxyz") == std::string::npos) {
            return false; // Password must contain at least one lowercase letter
        }
        if(password.find_first_of("ABCDEFGHIJKLMNOPQRSTUVWXYZ") == std::string::npos) {
            return false; // Password must contain at least one uppercase letter
        }

        return true;
    }
} // namespace encryption::password
