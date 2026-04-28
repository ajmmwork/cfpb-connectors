from datetime import datetime
import requests

def validate_date(date_str) -> str:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError(
            f"Invalid date '{date_str}'. Expected format YYYY-MM-DD (e.g., 2025-01-31)"
        )
    return date_str

from datetime import datetime
import requests
from typing import Any


def validate_date(date_str: str) -> str:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        raise ValueError(
            f"Invalid date '{date_str}'. Expected format YYYY-MM-DD (e.g., 2025-01-31)"
        )


def make_request(base_url: str, params: dict) -> list[dict[str, Any]]:
    try:
        response = requests.get(
            url=base_url,
            params=params,
            timeout=120
        )
    except requests.RequestException as e:
        raise RuntimeError(
            f"Failed to connect to CFPB API: {e}"
        ) from e

    if not response.ok:
        raise RuntimeError(
            f"CFPB API returned status {response.status_code}. "
            f"Check your parameters (companies={params.get('company')}, "
            f"date range={params.get('date_received_min')} to {params.get('date_received_max')})"
        )

    try:
        raw_data = response.json()
    except ValueError as e:
        raise RuntimeError(
            "CFPB API returned invalid JSON response"
        ) from e

    if not isinstance(raw_data, (dict, list)):
        raise RuntimeError(
            f"Unexpected response format from CFPB API: {type(raw_data).__name__}"
        )

    records: list[dict[str, Any]] = []

    # Case 1: list response
    if isinstance(raw_data, list):
        for item in raw_data:
            if not isinstance(item, dict):
                continue

            source = item.get("_source")
            records.append(source if isinstance(source, dict) else item)

    # Case 2: dict response (Elasticsearch-style)
    elif isinstance(raw_data, dict):
        page_hits = raw_data.get("hits", {}).get("hits", [])

        if not isinstance(page_hits, list):
            raise RuntimeError("Expected raw_data['hits']['hits'] to be a list")

        for item in page_hits:
            if not isinstance(item, dict):
                continue

            source = item.get("_source")
            if isinstance(source, dict):
                records.append(source)

    return records


def date_only(dt: str | None):
    return dt.split("T")[0] if isinstance(dt, str) else None
