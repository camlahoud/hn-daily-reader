#!/usr/bin/env python3
"""TEMPORARY diagnostic: probe the HN Algolia API with several request shapes
and print HTTP status + response body for each, so we can see exactly what the
API is now rejecting. Safe/read-only. Delete after diagnosis."""

import json
import urllib.request
import urllib.parse

BASE = "https://hn.algolia.com/api/v1/search"
START, END, MIN_POINTS = 1782259200, 1782345599, 100  # same window as a failing run


def probe(label, params):
    url = f"{BASE}?{urllib.parse.urlencode(params)}"
    print("\n" + "=" * 70)
    print(f"[{label}]")
    print(f"URL: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "HN-Daily-Reader/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode("utf-8", "replace")
            data = json.loads(body)
            print(f"  STATUS: {r.status} OK  nbHits={data.get('nbHits')} hits={len(data.get('hits', []))}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        print(f"  STATUS: {e.code} {e.reason}")
        print(f"  BODY: {body[:600]}")
    except Exception as e:  # noqa
        print(f"  ERROR: {type(e).__name__}: {e}")


# 1. The current (failing) comma-separated numericFilters
probe("comma numericFilters (current)", {
    "tags": "story",
    "numericFilters": f"created_at_i>={START},created_at_i<={END},points>={MIN_POINTS}",
    "hitsPerPage": 20,
})

# 2. JSON-array numericFilters (documented canonical form)
probe("json-array numericFilters", {
    "tags": "story",
    "numericFilters": json.dumps([f"created_at_i>={START}", f"created_at_i<={END}", f"points>={MIN_POINTS}"]),
    "hitsPerPage": 20,
})

# 3. Only points filter (no created_at) — isolates whether timestamp filter is the problem
probe("points-only numericFilters", {
    "tags": "story",
    "numericFilters": f"points>={MIN_POINTS}",
    "hitsPerPage": 2,
})

# 4. No filters at all — isolates whether the endpoint itself works
probe("no filters", {"tags": "story", "hitsPerPage": 2})

# 5. search_by_date variant with comma numericFilters
probe("search_by_date comma", {
    "tags": "story",
    "numericFilters": f"created_at_i>={START},created_at_i<={END},points>={MIN_POINTS}",
    "hitsPerPage": 20,
})
