import json
from pathlib import Path
from typing import Any, Dict

import pytest

from limitless_api import ApiError, LifelogClient, LifelogEntry, RateLimitError


@pytest.fixture(scope="module")
def sample_response() -> Dict[str, Any]:
    data_path = Path(__file__).parent / "data" / "lifelogs_sample.json"
    return json.loads(data_path.read_text(encoding="utf-8"))


@pytest.fixture
def client() -> LifelogClient:
    return LifelogClient(api_key="test-key", base_url="https://api.limitless.ai")


def test_client_requires_api_key() -> None:
    with pytest.raises(ValueError):
        LifelogClient(api_key="")


def test_sends_api_key_header(requests_mock, client: LifelogClient, sample_response) -> None:
    mock = requests_mock.get(
        "https://api.limitless.ai/v1/lifelogs",
        json=sample_response,
    )

    client.list_lifelogs(limit=1)

    assert mock.called
    assert mock.last_request.headers["X-API-Key"] == "test-key"


def test_builds_query_parameters(requests_mock, client: LifelogClient, sample_response) -> None:
    mock = requests_mock.get(
        "https://api.limitless.ai/v1/lifelogs",
        json=sample_response,
    )

    client.list_lifelogs(limit=10, date="2024-09-17", timezone="Asia/Tokyo")

    assert mock.last_request.qs["limit"] == ["10"]
    assert mock.last_request.qs["date"] == ["2024-09-17"]
    assert mock.last_request.qs["timezone"][0].lower() == "asia/tokyo"


def test_parses_lifelog_entries(requests_mock, client: LifelogClient, sample_response) -> None:
    requests_mock.get(
        "https://api.limitless.ai/v1/lifelogs",
        json=sample_response,
    )

    entries, next_cursor = client.list_lifelogs()

    assert next_cursor is None
    assert len(entries) == 1
    entry = entries[0]
    assert isinstance(entry, LifelogEntry)
    assert entry.id == "log_123"
    assert entry.title == "Morning standup"
    assert entry.start_time.isoformat() == "2024-09-17T00:00:00+00:00"
    assert entry.markdown.startswith("## Morning")
    assert entry.contents[0]["type"] == "heading1"


def test_handles_rate_limit_error(requests_mock, client: LifelogClient) -> None:
    requests_mock.get(
        "https://api.limitless.ai/v1/lifelogs",
        json={"error": "API key is rate limited", "retryAfter": "60"},
        status_code=429,
    )

    with pytest.raises(RateLimitError) as exc:
        client.list_lifelogs()

    assert exc.value.status_code == 429
    assert exc.value.retry_after == 60
    assert "rate limited" in exc.value.message


def test_handles_generic_api_error(requests_mock, client: LifelogClient) -> None:
    requests_mock.get(
        "https://api.limitless.ai/v1/lifelogs",
        json={"error": "Service unavailable"},
        status_code=500,
    )

    with pytest.raises(ApiError) as exc:
        client.list_lifelogs()

    assert exc.value.status_code == 500
    assert "Service unavailable" in exc.value.message
