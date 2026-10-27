import uuid

import pytest

from tests.api_client import ApiClient


@pytest.fixture(scope="session")
def playground() -> ApiClient:
    return ApiClient(
        "https://playground.nileslabs.com/api/v1",
        identity=f"lab2-{uuid.uuid4()}",
    )
