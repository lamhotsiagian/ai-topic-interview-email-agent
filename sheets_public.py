import csv
import io
from dataclasses import dataclass
from typing import List, Dict, Optional

import requests


@dataclass
class SheetRow:
    raw: Dict[str, str]


def fetch_public_sheet_rows(csv_url: str, timeout_sec: int = 30) -> List[SheetRow]:
    """
    Fetch a PUBLIC Google Sheet as CSV (no login).
    Returns rows as dicts keyed by header columns.
    """
    r = requests.get(csv_url, timeout=timeout_sec)
    r.raise_for_status()

    reader = csv.DictReader(io.StringIO(r.text))
    rows: List[SheetRow] = []
    for row in reader:
        rows.append(SheetRow(raw={k.strip(): (v or "").strip() for k, v in row.items() if k}))
    return rows


def extract_topics(rows: List[SheetRow], topic_col: str) -> List[str]:
    topics: List[str] = []
    for r in rows:
        match_key: Optional[str] = None
        for k in r.raw.keys():
            if k.strip().lower() == topic_col.strip().lower():
                match_key = k
                break

        if not match_key:
            continue

        t = (r.raw.get(match_key) or "").strip()
        if t:
            topics.append(t)

    return topics
