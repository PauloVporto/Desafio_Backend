import os
import uuid

import django
import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from app.database import engine
from app.products.repository import ProductRepository


@pytest.fixture(scope="session", autouse=True)
def verify_services():
    with engine.connect() as connection:
        connection.exec_driver_sql("SELECT 1")

    repo = ProductRepository()
    try:
        repo.client.admin.command("ping")
    finally:
        repo.close()


@pytest.fixture
def test_user_data():
    suffix = uuid.uuid4().hex[:10]
    return {
        "username": f"teste_{suffix}",
        "password": "Senha123!",
        "email": f"{suffix}@example.com",
    }
