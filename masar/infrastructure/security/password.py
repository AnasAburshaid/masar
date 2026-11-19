"""Secure password hashing and verification utilities using PBKDF2-HMAC-SHA256."""

import hashlib
import hmac
import secrets

from masar.application.interfaces.security.password_hasher import PasswordHasher

DEFAULT_ITERATIONS = 100_000
SALT_SIZE = 16


def hash_password(plain_password: str, iterations: int = DEFAULT_ITERATIONS) -> str:
    """Hash a plaintext password using PBKDF2-HMAC-SHA256 with a random salt."""
    if not plain_password:
        raise ValueError("Password cannot be empty.")
    salt = secrets.token_bytes(SALT_SIZE)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt,
        iterations,
    )
    salt_hex = salt.hex()
    key_hex = key.hex()
    return f"pbkdf2:sha256:{iterations}${salt_hex}${key_hex}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored hashed password."""
    if not plain_password or not hashed_password:
        return False
    try:
        parts = hashed_password.split("$")
        if len(parts) != 3:
            return False
        header, salt_hex, expected_key_hex = parts
        algorithm_parts = header.split(":")
        if len(algorithm_parts) != 3:
            return False
        method, hash_algo, iterations_str = algorithm_parts
        if method != "pbkdf2" or hash_algo != "sha256":
            return False
        iterations = int(iterations_str)
        salt = bytes.fromhex(salt_hex)
        expected_key = bytes.fromhex(expected_key_hex)

        computed_key = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt,
            iterations,
        )
        return hmac.compare_digest(computed_key, expected_key)
    except Exception:
        return False


class Pbkdf2PasswordHasher(PasswordHasher):
    """Concrete implementation of PasswordHasher using PBKDF2-HMAC-SHA256."""

    def __init__(self, iterations: int = DEFAULT_ITERATIONS) -> None:
        self._iterations = iterations

    def hash(self, plain_password: str) -> str:
        return hash_password(plain_password, iterations=self._iterations)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return verify_password(plain_password, hashed_password)
