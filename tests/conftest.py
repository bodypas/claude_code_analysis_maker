import pytest

from src.dashboard.app import app


@pytest.fixture
def dash_app():
    return app
