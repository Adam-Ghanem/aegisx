from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

AuditValue = str | int | float | bool | None
_SENSITIVE = (
    "password",
    "passwd",
    "token",
    "secret",
    "credential",
    "authorization",
    "cookie",
    "raw_event",
)


@dataclass(frozen=True, slots=True)
class AuditMetadata:
    """Bounded scalar-only metadata safe for audit envelopes."""

    values: Mapping[str, AuditValue]

    def __post_init__(self) -> None:
        if len(self.values) > 32:
            raise ValueError("audit metadata has too many fields")
        copied: dict[str, AuditValue] = {}
        for key, value in self.values.items():
            normalized = key.casefold().replace("-", "_")
            if not key or len(key) > 64 or any(part in normalized for part in _SENSITIVE):
                raise ValueError("sensitive or invalid audit metadata key")
            if not isinstance(value, str | int | float | bool | None):
                raise TypeError("audit metadata values must be scalar")
            if isinstance(value, str) and len(value) > 512:
                raise ValueError("audit metadata value is too long")
            copied[key] = value
        object.__setattr__(self, "values", copied)

    def as_dict(self) -> dict[str, AuditValue]:
        return dict(self.values)
