#!/usr/bin/env python3
"""ニュースRSSを取得し、フロントエンド用のJSONを書き出す。

GitHub ActionsのPagesデプロイ前に実行され、news-app/data/{category}.json を生成する。
ブラウザ側ではこの静的JSONを取得するだけなので、CORSプロキシ等は不要。
"""
import datetime as dt
import email.utils
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import quote

# 動画ベースのニュースサイト（記事ではなくプレイヤー中心）
VIDEO_DOMAINS = {
    "tbs.co.jp",        # TBS NEWS DIG など
    "tv-asahi.co.jp",   # テレ朝news
    "fnn.jp",           # FNNプライムオンライン
    "ntv.co.jp",        # 日テレNEWS
    "nnn.co.jp",        # 日テレ系NNN
    "yahoo.co.jp",      # Yahoo!（オリジナル記事へ飛ぶがリンク切れも多い）
    "youtube.com",
    "youtu.be",
}

# 有料記事中心のサイト（無料部分のみ提供する媒体も含む）
PAYWALL_DOMAINS = {
    "nikkei.com",       # 日経電子版
    "asahi.com",        # 朝日新聞デジタル（digital.asahi.com含む）
    "mainichi.jp",      # 毎日新聞 / 毎日新聞プレミア
    "yomiuri.co.jp",    # 読売新聞オンライン（会員限定多数）
    "bloomberg.co.jp",  # ブルームバーグ日本
    "wsj.com",          # WSJ Japan / WSJ
    "ft.com",           # Financial Times
    "bunshun.jp",       # 週刊文春
    "gendai.media",     # 現代ビジネス
    "diamond.jp",       # ダイヤモンド・オンライン
    "toyokeizai.net",   # 東洋経済オンライン
    "president.jp",     # PRESIDENT Online
    "shogakukan.co.jp", # 小学館系（NEWSポストセブン等）
    "newspostseven.com",
}

EXCLUDE_DOMAINS = VIDEO_DOMAINS | PAYWALL_DOMAINS

# 動画・ライブ中継のキーワード
VIDEO_KEYWORDS = re.compile(
    r"(\[?動画\]?|【動画】|ＬＩＶＥ|【LIVE】|【ライブ】|生中継|ライブ配信|ノーカット|"
    r"ニュース動画|現場中継|記者会見\s*ライブ)"
)

# 有料記事のキーワード（タイトルに含まれていれば除外）
PAYWALL_KEYWORDS = re.compile(
    r"(\(有料(?:記事|会員)?\)|（有料(?:記事|会員)?）|\[有料\]|【有料】|"
    r"有料会員|会員限定|会員専用|プレミアム会員|プレミア記事|プレミアム記事|"
    r"メンバー限定|サブスク(?:会員|限定)?|有料配信|有料閲覧|Premium)"
)

EXCLUDE_QUERY = " ".join(f"-site:{s}" for s in sorted(EXCLUDE_DOMAINS))


def build_url(query: str) -> str:
    # 直近24時間の記事に絞る（最新ニュース重視）
    q = f"{query} when:1d {EXCLUDE_QUERY}"
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
        pub_raw = (node.findtext("pubDate") or "").strip()
        items.append({
            "title":   (node.findtext("title") or "").strip(),
            "link":    (node.findtext("link") or "").strip(),
            "pubDate": pub_raw,
            "pubTimestamp": parse_pubdate(pub_raw),
            "sourceUrl":  source_url.strip(),
            "sourceName": source_name.strip(),
        })
    return items


def parse_pubdate(s: str) -> float:
    """RFC2822形式の pubDate を Unix epoch 秒に変換。失敗時は 0。"""
    if not s:
        return 0.0
    try:
        d = email.utils.parsedate_to_datetime(s)
        if d.tzinfo is None:
            d = d.replace(tzinfo=dt.timezone.utc)
        return d.timestamp()
    except (TypeError, ValueError):
        return 0.0


def is_article(item: dict) -> bool:
    title = item.get("title", "")
    if VIDEO_KEYWORDS.search(title):
        return False
    if PAYWALL_KEYWORDS.search(title):
        return False
    src = item.get("sourceUrl", "")
    if src:
        host = (urllib.parse.urlparse(src).hostname or "").lower()
        if host in EXCLUDE_DOMAINS:
            return False
        # サブドメインも除外（例: digital.asahi.com → asahi.com）
        for d in EXCLUDE_DOMAINS:
            if host.endswith("." + d):
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
        # 新しい順にソート
        items.sort(key=lambda i: i.get("pubTimestamp", 0), reverse=True)
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
