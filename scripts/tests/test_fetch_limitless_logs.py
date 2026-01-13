import json
from pathlib import Path

import pytest

import scripts.fetch_limitless_logs as fetcher


class DummyClient:
    def __init__(self, pages):
        self._pages = list(pages)
        self.calls = []

    def list_lifelogs(self, **params):
        self.calls.append(params)
        if not self._pages:
            return [], None
        item = self._pages.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


class DummyEntry:
    def __init__(self, id_: str):
        self.id = id_
        self.title = "t"
        self.start_time = type("T", (), {"isoformat": lambda self: "s"})()
        self.end_time = type("T", (), {"isoformat": lambda self: "e"})()
        self.updated_at = type("T", (), {"isoformat": lambda self: "u"})()
        self.is_starred = False
        self.markdown = None
        self.contents = []


def test_load_existing_ids(tmp_path: Path) -> None:
    (tmp_path / "log_1.json").write_text("{}", encoding="utf-8")
    (tmp_path / "log_2.json").write_text("{}", encoding="utf-8")
    ids = fetcher.load_existing_ids(tmp_path)
    assert ids == {"log_1", "log_2"}


def test_save_entries_skips_duplicates(tmp_path: Path) -> None:
    out = tmp_path
    seen = {"log_1"}
    entries = [DummyEntry("log_1"), DummyEntry("log_2")]

    saved = fetcher.save_entries(entries, out, seen)

    assert saved == 1
    assert (out / "log_2.json").exists()
    payload = json.loads((out / "log_2.json").read_text(encoding="utf-8"))
    assert payload["id"] == "log_2"


def test_rate_limiter_waits(monkeypatch) -> None:
    # Monotonic advances in controlled steps.
    times = iter([0.0, 0.0, 0.005, 0.02])

    def fake_monotonic():
        return next(times)

    slept = []

    def fake_sleep(x: float) -> None:
        slept.append(x)

    monkeypatch.setattr(fetcher.time, "monotonic", fake_monotonic)
    monkeypatch.setattr(fetcher.time, "sleep", fake_sleep)

    limiter = fetcher.RateLimiter(100.0)  # min interval 0.01s
    limiter.wait()  # initializes
    limiter.wait()  # should sleep ~0.01

    assert slept
    assert slept[0] == pytest.approx(0.01, abs=1e-6)


def test_fetch_with_retry_paginates_and_throttles(monkeypatch) -> None:
    limiter_calls = 0

    class CountingLimiter:
        def wait(self):
            nonlocal limiter_calls
            limiter_calls += 1

    e1 = DummyEntry("log_1")
    e2 = DummyEntry("log_2")
    client = DummyClient(
        pages=[
            ([e1], "c1"),
            ([e2], None),
        ]
    )

    pages = list(
        fetcher.fetch_with_retry(
            client,
            limit=10,
            date=None,
            start=None,
            end=None,
            timezone=None,
            max_retries=1,
            backoff_seconds=0.0,
            max_backoff_seconds=0.0,
            rate_limiter=CountingLimiter(),
        )
    )

    assert [len(p) for p in pages] == [1, 1]
    assert limiter_calls == 2
    assert client.calls[0]["cursor"] is None
    assert client.calls[1]["cursor"] == "c1"


def test_fetch_with_retry_passes_filters() -> None:
    class NoWaitLimiter:
        def wait(self):
            return None

    e1 = DummyEntry("log_1")
    client = DummyClient(pages=[([e1], None)])

    list(
        fetcher.fetch_with_retry(
            client,
            limit=10,
            date="2024-09-17",
            start=None,
            end=None,
            timezone="Asia/Tokyo",
            max_retries=1,
            backoff_seconds=0.0,
            max_backoff_seconds=0.0,
            rate_limiter=NoWaitLimiter(),
        )
    )

    assert client.calls[0]["date"] == "2024-09-17"
    assert client.calls[0]["timezone"] == "Asia/Tokyo"


def test_fetch_with_retry_retries_on_timeout(monkeypatch) -> None:
    # Make backoff a no-op.
    monkeypatch.setattr(fetcher, "_sleep_with_backoff", lambda *_args, **_kw: None)

    class NoWaitLimiter:
        def wait(self):
            return None

    timeout_exc = fetcher.requests.exceptions.Timeout("t")
    e1 = DummyEntry("log_1")
    client = DummyClient(pages=[timeout_exc, ([e1], None)])

    pages = list(
        fetcher.fetch_with_retry(
            client,
            limit=10,
            date=None,
            start=None,
            end=None,
            timezone=None,
            max_retries=2,
            backoff_seconds=0.0,
            max_backoff_seconds=0.0,
            rate_limiter=NoWaitLimiter(),
        )
    )

    assert len(pages) == 1
    assert pages[0][0].id == "log_1"
    assert len(client.calls) == 2


def test_iter_pages_all_data_falls_back_when_empty_and_no_filters(monkeypatch) -> None:
    # Stabilize "now".
    monkeypatch.setattr(fetcher, "_utc_now_z", lambda: "2026-01-13T00:00:00Z")

    class NoWaitLimiter:
        def wait(self):
            return None

    e1 = DummyEntry("log_1")
    client = DummyClient(
        pages=[
            ([], None),
            ([e1], None),
        ]
    )

    pages = list(
        fetcher.iter_pages_all_data(
            client,
            limit=10,
            date=None,
            start=None,
            end=None,
            timezone_name=None,
            max_retries=1,
            backoff_seconds=0.0,
            max_backoff_seconds=0.0,
            rate_limiter=NoWaitLimiter(),
        )
    )

    assert len(pages) == 1
    assert pages[0][0].id == "log_1"
    assert len(client.calls) == 2
    assert client.calls[1]["start"] == "1970-01-01T00:00:00Z"
    assert client.calls[1]["end"] == "2026-01-13T00:00:00Z"
    assert client.calls[1]["timezone"] == "UTC"


def test_iter_pages_all_data_does_not_fall_back_when_filters_provided() -> None:
    class NoWaitLimiter:
        def wait(self):
            return None

    client = DummyClient(pages=[([], None)])
    pages = list(
        fetcher.iter_pages_all_data(
            client,
            limit=10,
            date="2024-09-17",
            start=None,
            end=None,
            timezone_name="Asia/Tokyo",
            max_retries=1,
            backoff_seconds=0.0,
            max_backoff_seconds=0.0,
            rate_limiter=NoWaitLimiter(),
        )
    )

    assert pages == [[]]
    assert len(client.calls) == 1
