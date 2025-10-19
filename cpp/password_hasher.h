// password_hasher.h
// Public API for password hashing and password validation exposed to Python.
// All other helpers remain internal to C++ and are not bound to Python.

#pragma once
#include <string>
#include <vector>
#include <optional>

namespace encryption::password {

// Generate a random salt string for password hashing
// Parameters:
//  - bytes: length of the salt string (default: 16)
std::string generate_salt(std::size_t bytes = 16);

// Main hashing function. Returns the final hashed password string.
// Parameters:
//  - password: input string to hash
//  - cost: iteration cost factor (effective iterations = 2^cost)
//  - salt: optional salt string; if not provided, generates a random salt
std::string hash_password(const std::string& password, int cost = 2, std::optional<std::string> salt = std::nullopt);

// Password validator: returns true if the password meets basic strength requirements.
bool check_password_strength(const std::string& password);

} // namespace encryption::password
