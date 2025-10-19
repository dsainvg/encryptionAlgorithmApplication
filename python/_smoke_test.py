import time
import encryption_backend as backend  # pyright: ignore[reportMissingImports]


def main():
    password = "Secret123!@#"
    cost = 12
    t0 = time.perf_counter()
    result = backend.hash_password(password, cost)
    dt = (time.perf_counter() - t0) * 1000.0
    print(f"hash_password(cost={cost}) took {dt:.2f} ms")
    print("RESULT:", result[:100] + "..." if len(result) > 100 else result)
    print("Password strength OK?", backend.check_password_strength(password))


if __name__ == "__main__":
    main()
