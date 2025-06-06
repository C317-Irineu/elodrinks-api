import os

os.environ["MERCADO_PAGO_ACCESS_TOKEN"] = "dummy_token_de_teste"
os.environ["EMAIL_PORT"] = "587"

import pytest
from fastapi.testclient import TestClient

from main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c
