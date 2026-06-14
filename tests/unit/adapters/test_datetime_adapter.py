from datetime import UTC, datetime

from app.adapters.datetime_adapter import to_aware, to_naive

AWARE = datetime(2026, 6, 4, 12, 0, tzinfo=UTC)
NAIVE = datetime(2026, 6, 4, 12, 0)


# --- to_naive ---


def test_to_naive_strips_timezone():
    result = to_naive(AWARE)

    assert result == NAIVE
    assert result.tzinfo is None


def test_to_naive_returns_none_for_none():
    assert to_naive(None) is None


def test_to_naive_passthrough_on_already_naive():
    result = to_naive(NAIVE)

    assert result == NAIVE
    assert result.tzinfo is None


# --- to_aware ---


def test_to_aware_attaches_utc():
    result = to_aware(NAIVE)

    assert result == AWARE
    assert result.tzinfo is UTC


def test_to_aware_returns_none_for_none():
    assert to_aware(None) is None


def test_to_aware_replaces_existing_timezone():
    from datetime import timedelta, timezone

    other_tz = timezone(timedelta(hours=3))
    dt = datetime(2026, 6, 4, 12, 0, tzinfo=other_tz)

    result = to_aware(dt)

    assert result.tzinfo is UTC
