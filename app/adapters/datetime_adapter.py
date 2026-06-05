from datetime import UTC, datetime


def to_naive(dt: datetime | None) -> datetime | None:
    return dt.replace(tzinfo=None) if dt is not None else None


def to_aware(dt: datetime | None) -> datetime | None:
    return dt.replace(tzinfo=UTC) if dt is not None else None
