// binding.cpp
// pybind11 module to expose password hashing and encryption functions to Python.
// Build will produce a Python extension module (e.g., encryption_backend.pyd on Windows).

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include "password_hasher.h"
#include "crypto_operations.h"

namespace py = pybind11;

PYBIND11_MODULE(encryption_backend, m) {
    m.doc() = "Password hashing and encryption operations for secure file protection";

    // Password hashing functions
    m.def("generate_salt", &encryption::password::generate_salt,
        "Generate a random salt string for password hashing.",
        py::arg("bytes") = 16);
        
    m.def("hash_password", &encryption::password::hash_password,
        "Hash a password using custom algorithm; returns final hashed password string.",
        py::arg("password"), py::arg("cost") = 2, py::arg("salt") = py::none());
        
    m.def("check_password_strength", &encryption::password::check_password_strength,
        "Check password strength (meets security policy requirements).", 
        py::arg("password"));


    // Advanced encryption operations
    m.def("encrypt_data", [](py::bytes data, py::bytes key, int rounds) -> py::bytes {
        std::string str_data = data;
        std::string str_key = key;
        std::string result = encryption::crypto::encrypt_data(str_data, str_key, rounds);
        return py::bytes(result);
    }, "Encrypt data using multiple rounds of XOR and bit rotation",
       py::arg("data"), py::arg("key"), py::arg("rounds") = 1);

    m.def("decrypt_data", [](py::bytes encrypted_data, py::bytes key, int rounds) -> py::bytes {
        std::string str_data = encrypted_data;
        std::string str_key = key;
        std::string result = encryption::crypto::decrypt_data(str_data, str_key, rounds);
        return py::bytes(result);
    }, "Decrypt data using multiple rounds of reverse operations",
       py::arg("encrypted_data"), py::arg("key"), py::arg("rounds") = 1);
}
