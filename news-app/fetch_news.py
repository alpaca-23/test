#!/usr/bin/env python3
"""ニュースRSSを取得し、フロントエンド用のJSONを書き出す。

GitHub ActionsのPagesデプロイ前に実行され、news-app/data/{category}.json を生成する。
ブラウザ側ではこの静的JSONを取得するだけなので、CORSプロキシ等は不要。
"""
import datetime as dt
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import quote

# 動画ベースのニュースサイト（記事ではなくプレイヤー中心）を除外する
EXCLUDE_SITES = [
    "newsdig.tbs.co.jp",        # TBS NEWS DIG
    "news.tv-asahi.co.jp",      # テレ朝news
    "www.fnn.jp",               # FNNプライムオンライン
    "news.ntv.co.jp",           # 日テレNEWS
    "www.nnn.co.jp",            # 日テレ系NNN
    "news.yahoo.co.jp",         # Yahoo!（オリジナル記事へ飛ぶがリンク切れが多い）
    "www.youtube.com",
    "youtu.be",
]

EXCLUDE_DOMAINS = set(EXCLUDE_SITES)

# 動画・ライブ中継のキーワード
VIDEO_KEYWORDS = re.compile(
    r"(\[?動画\]?|【動画】|ＬＩＶＥ|【LIVE】|【ライブ】|生中継|ライブ配信|ノーカット|"
    r"ニュース動画|現場中継|記者会見\s*ライブ)"
)

EXCLUDE_QUERY = " ".join(f"-site:{s}" for s in EXCLUDE_SITES)


def build_url(query: str) -> str:
    q = f"{query} when:2d {EXCLUDE_QUERY}"
    return (
        "https://news.google.com/rss/search?q="
        + quote(q)
        + "&hl=ja&gl=JP&ceid=JP:ja"
    )


FEEDS = {
    "politics":  build_url("日本 政治"),
    "economics": build_url("日本 経済"),
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
        source_el = node.find("source")
        source_url = (source_el.get("url") if source_el is not None else "") or ""
        source_name = (source_el.text if source_el is not None else "") or ""
        items.append({
            "title":   (node.findtext("title") or "").strip(),
            "link":    (node.findtext("link") or "").strip(),
            "pubDate": (node.findtext("pubDate") or "").strip(),
            "sourceUrl":  source_url.strip(),
            "sourceName": source_name.strip(),
        })
    return items


def is_article(item: dict) -> bool:
    if VIDEO_KEYWORDS.search(item.get("title", "")):
        return False
    src = item.get("sourceUrl", "")
    if src:
        host = urllib.parse.urlparse(src).hostname or ""
        if host in EXCLUDE_DOMAINS:
            return False
        # サブドメイン違いも除外
        for d in EXCLUDE_DOMAINS:
            if host.endswith("." + d) or host == d:
                return False
    return True


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
        before = len(items)
        items = [i for i in items if is_article(i)]
        out = OUT_DIR / f"{name}.json"
        out.write_text(
            json.dumps(
                {"fetched_at": fetched_at, "items": items},
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"  wrote {out.name} ({len(items)}/{before} items after filter)")
    return 1 if failures == len(FEEDS) else 0


if __name__ == "__main__":
    sys.exit(main())
