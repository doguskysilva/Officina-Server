from app.main import hello


def test_hello_returns_message():
    assert hello() == {"message": "Hello, World!"}
