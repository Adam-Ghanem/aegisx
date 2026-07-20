"""Password hashing using the memory-hard scrypt KDF from the standard library."""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PasswordHasher:
    """Create self-describing hashes and verify them in constant time."""

    n: int = 2**14
    r: int = 8
    p: int = 1
    salt_bytes: int = 16
    key_bytes: int = 32

    def hash(self, password: str) -> str:
        self._validate_password(password)
        salt = secrets.token_bytes(self.salt_bytes)
        derived = hashlib.scrypt(
            password.encode("utf-8"), salt=salt, n=self.n, r=self.r, p=self.p, dklen=self.key_bytes
        )
        return "$".join(
            (
                "scrypt",
                str(self.n),
                str(self.r),
                str(self.p),
                base64.urlsafe_b64encode(salt).decode("ascii").rstrip("="),
                base64.urlsafe_b64encode(derived).decode("ascii").rstrip("="),
            )
        )

    def verify(self, password: str, encoded: str) -> bool:
        try:
            algorithm, n, r, p, salt, expected = encoded.split("$")
            if algorithm != "scrypt":
                return False
            work_n, block_r, parallel_p = int(n), int(r), int(p)
            if work_n > self.n or block_r > self.r or parallel_p > self.p:
                return False
            if work_n < 2 or work_n & (work_n - 1) or block_r < 1 or parallel_p < 1:
                return False
            salt_bytes = _decode(salt)
            expected_bytes = _decode(expected)
            if len(salt_bytes) > 64 or not 16 <= len(expected_bytes) <= 64:
                return False
            actual = hashlib.scrypt(
                password.encode("utf-8"),
                salt=salt_bytes,
                n=work_n,
                r=block_r,
                p=parallel_p,
                dklen=len(expected_bytes),
            )
            return hmac.compare_digest(actual, expected_bytes)
        except (UnicodeError, ValueError):
            return False

    def needs_rehash(self, encoded: str) -> bool:
        try:
            algorithm, n, r, p, _salt, _derived = encoded.split("$")
            return (algorithm, int(n), int(r), int(p)) != ("scrypt", self.n, self.r, self.p)
        except ValueError:
            return True

    @staticmethod
    def _validate_password(password: str) -> None:
        if not isinstance(password, str) or not password or len(password.encode("utf-8")) > 1024:
            raise ValueError("password must contain between 1 and 1024 UTF-8 bytes")


def _decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
