from app.lambda_handler import handler


def test_lambda_handler_imports() -> None:
    assert handler is not None
