from app.main import health, hello


def test_hello_returns_message():
    assert hello() == {"message": "Hello, World!"}


def test_health_returns_ok():
    assert health() == {"status": "ok"}
