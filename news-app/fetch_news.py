#!/usr/bin/env python3
"""ニュースRSSを取得し、フロントエンド用のJSONを書き出す。

GitHub ActionsのPagesデプロイ前に実行され、news-app/data/{category}.json を生成する。
ブラウザ側ではこの静的JSONを取得するだけなので、CORSプロキシ等は不要。
"""
import datetime as dt
import json
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import quote

FEEDS = {
    "politics":  "https://news.google.com/rss/search?q={q}&hl=ja&gl=JP&ceid=JP:ja".format(
        q=quote("日本 政治 when:2d")
    ),
    "economics": "https://news.google.com/rss/search?q={q}&hl=ja&gl=JP&ceid=JP:ja".format(
        q=quote("日本 経済 when:2d")
    ),
}

OUT_DIR = Path(__file__).parent / "data"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse(xml: str) -> list[dict]:
    root = ET.fromstring(xml)
    items = []
    for node in root.iter("item"):
        items.append({
            "title":   (node.findtext("title") or "").strip(),
            "link":    (node.findtext("link") or "").strip(),
            "pubDate": (node.findtext("pubDate") or "").strip(),
        })
    return items


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fetched_at = dt.datetime.now(dt.timezone.utc).isoformat()
    failures = 0
    for name, url in FEEDS.items():
        print(f"[{name}] fetching {url}")
        try:
            xml = fetch(url)
            items = parse(xml)
        except (urllib.error.URLError, ET.ParseError) as err:
            print(f"  ERROR: {err}", file=sys.stderr)
            failures += 1
            continue
        out = OUT_DIR / f"{name}.json"
        out.write_text(
            json.dumps(
                {"fetched_at": fetched_at, "items": items},
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"  wrote {out.name} ({len(items)} items)")
    return 1 if failures == len(FEEDS) else 0


if __name__ == "__main__":
    sys.exit(main())
