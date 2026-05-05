"""Smoke test to verify pytest is configured correctly."""


def test_smoke():
    """Basic sanity check."""
    assert 1 + 1 == 2


def test_imports():
    """Verify the app package can be imported."""
    from app import create_app
    app = create_app()
    assert app is not None