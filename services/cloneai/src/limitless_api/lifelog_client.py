"""Lifelog API client placeholder for TDD."""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Tuple

import requests


class ApiError(Exception):
    """Base class for Limitless API errors."""

    def __init__(self, message: str, status_code: int, payload: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}


class RateLimitError(ApiError):
    """Specific error that carries retry-after hints."""

    def __init__(self, message: str, status_code: int, retry_after: Optional[int] = None, payload: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code, payload)
        self.retry_after = retry_after


@dataclass
class LifelogEntry:
    id: str
    title: str
    start_time: datetime
    end_time: datetime
    is_starred: bool
    updated_at: datetime
    markdown: Optional[str]
    contents: List[Dict[str, Any]]


class LifelogClient:
    """Small helper for calling the Limitless lifelog API."""

    _PATH_LIFELOGS = "/v1/lifelogs"

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.limitless.ai",
        session: Optional[requests.Session] = None,
        timeout: float = 30.0,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self._session = session or requests.Session()
        self._timeout = timeout

    def list_lifelogs(self, **params: Any) -> Tuple[List[LifelogEntry], Optional[str]]:
        """Fetch a page of lifelog entries with optional filters."""

        url = f"{self.base_url}{self._PATH_LIFELOGS}"
        query = {k: v for k, v in params.items() if v is not None}
        headers = {"X-API-Key": self.api_key}

        response = self._session.get(url, params=query, headers=headers, timeout=self._timeout)

        if response.status_code == 429:
            payload = _safe_json(response)
            retry_after = _extract_retry_after(payload)
            message = payload.get("error", "Too many requests")
            raise RateLimitError(message=message, status_code=429, retry_after=retry_after, payload=payload)

        if response.status_code >= 400:
            payload = _safe_json(response)
            message = payload.get("error") or response.text or "Limitless API error"
            raise ApiError(message=message, status_code=response.status_code, payload=payload)

        data = response.json()
        entries_json = data.get("lifelogs", [])
        entries = [_lifelog_from_json(item) for item in entries_json]
        return entries, data.get("nextCursor")


def _lifelog_from_json(payload: Dict[str, Any]) -> LifelogEntry:
    return LifelogEntry(
        id=payload.get("id", ""),
        title=payload.get("title", ""),
        start_time=_parse_iso8601(payload.get("startTime")),
        end_time=_parse_iso8601(payload.get("endTime")),
        is_starred=bool(payload.get("isStarred")),
        updated_at=_parse_iso8601(payload.get("updatedAt")),
        markdown=payload.get("markdown"),
        contents=payload.get("contents") or [],
    )


def _parse_iso8601(value: Optional[str]) -> datetime:
    if not value:
        return datetime.fromtimestamp(0, tz=datetime.UTC)
    # `fromisoformat` cannot parse trailing Z, so convert to +00:00 beforehand.
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


def _safe_json(response: requests.Response) -> Dict[str, Any]:
    try:
        return response.json()
    except ValueError:
        return {}


def _extract_retry_after(payload: Dict[str, Any]) -> Optional[int]:
    raw = payload.get("retryAfter")
    if raw is None:
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def _limit_arg(value: str) -> int:
    parsed = int(value)
    if parsed < 1 or parsed > 10:
        raise argparse.ArgumentTypeError("limit must be between 1 and 10")
    return parsed


def _format_entry(entry: LifelogEntry) -> str:
    lines = [
        f"ID: {entry.id}",
        f"Title: {entry.title}",
        f"Window: {entry.start_time.isoformat()} -> {entry.end_time.isoformat()}",
        f"Starred: {entry.is_starred}",
        f"Updated: {entry.updated_at.isoformat()}",
    ]
    if entry.markdown:
        lines.append("Markdown (first lines):")
        for snippet in entry.markdown.strip().splitlines()[:5]:
            lines.append(f"  {snippet}")
    return "\n".join(lines)


def _cli(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch Limitless Lifelog entries and print them to stdout.")
    parser.add_argument("--api-key", default=os.getenv("LIMITLESS_API_KEY"), help="APIキーを指定 (環境変数 LIMITLESS_API_KEY が既定)")
    parser.add_argument("--base-url", default="https://api.limitless.ai", help="APIベースURL (通常は既定値でOK)")
    parser.add_argument("--limit", type=_limit_arg, default=5, help="取得件数 1-10。既定は5件。")
    parser.add_argument("--date", help="ISO日付 (例: 2024-09-17)。指定するとその日のLifelogに限定")
    parser.add_argument("--start", help="ISO8601開始時刻。dateと併用しない場合はISO8601文字列")
    parser.add_argument("--end", help="ISO8601終了時刻")
    parser.add_argument("--timezone", help="タイムゾーンID (例: Asia/Tokyo)")
    parser.add_argument("--cursor", help="カーソル文字列。ページ送りしたいときに使用")

    args = parser.parse_args(argv)

    if not args.api_key:
        parser.error("APIキーが見つかりません。--api-key か LIMITLESS_API_KEY を設定してください。")

    client = LifelogClient(api_key=args.api_key, base_url=args.base_url)

    try:
        entries, next_cursor = client.list_lifelogs(
            limit=args.limit,
            date=args.date,
            start=args.start,
            end=args.end,
            timezone=args.timezone,
            cursor=args.cursor,
        )
    except RateLimitError as exc:
        print(f"Rate limited: {exc.message} (retryAfter={exc.retry_after})", file=sys.stderr)
        return 2
    except ApiError as exc:
        print(f"API error ({exc.status_code}): {exc.message}", file=sys.stderr)
        return 1

    if not entries:
        print("Lifelogエントリは見つかりませんでした。")
    else:
        for idx, entry in enumerate(entries, start=1):
            print(f"--- Entry {idx} ---")
            print(_format_entry(entry))
            print()

    if next_cursor:
        print(f"Next cursor: {next_cursor}")

    return 0


def main() -> None:
    sys.exit(_cli())


if __name__ == "__main__":
    main()
