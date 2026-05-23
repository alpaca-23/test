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

# 有料記事中心のサイト（拾わない）
PAYWALL_DOMAINS = {
    "nikkei.com",       # 日経電子版
    "asahi.com",        # 朝日新聞デジタル（digital.asahi.com含む）
    "mainichi.jp",      # 毎日新聞 / プレミア
    "yomiuri.co.jp",    # 読売新聞オンライン
    "bloomberg.co.jp",  # ブルームバーグ日本
    "wsj.com",          # WSJ Japan / WSJ
    "ft.com",           # Financial Times
    "bunshun.jp",       # 週刊文春
    "gendai.media",     # 現代ビジネス
    "diamond.jp",       # ダイヤモンド・オンライン
    "toyokeizai.net",   # 東洋経済オンライン
    "president.jp",     # PRESIDENT Online
}

# 軽量・タブロイド・芸能寄りのサイト（有料媒体の深掘り記事に比べ薄い）
TABLOID_DOMAINS = {
    "hochi.news",            # スポーツ報知
    "hochi.co.jp",
    "nikkansports.com",      # 日刊スポーツ
    "tokyo-sports.co.jp",    # 東スポWEB
    "daily.co.jp",           # デイリースポーツ
    "sponichi.co.jp",        # スポニチ
    "jprime.jp",             # 週刊女性PRIME
    "josei7.com",            # 女性自身
    "shujoseven.com",
    "friday.kodansha.co.jp", # FRIDAY DIGITAL
    "cyzo.com",              # サイゾー
    "cyzowoman.com",
    "excite.co.jp",          # エキサイトニュース
    "livedoor.com",          # livedoorニュース（アグリゲータ）
    "smt.docomo.ne.jp",      # dメニューニュース
    "biz-journal.jp",        # Business Journal（センセーショナル傾向）
    "j-cast.com",            # J-CAST
    "myjitsu.jp",            # 日刊大衆
    "asagei.com",            # 週刊アサヒ芸成
    "news-postseven.com",
    "newspostseven.com",
    "shukan-jitsuwa.com",    # 週刊実話
    "tocana.jp",             # TOCANA
    "ldnews.jp",
    "iza.ne.jp",             # 産経イザ！（センセーショナル傾向）
    "ironna.jp",
    "tanteifile.com",
    "smart-flash.jp",        # SmartFLASH
    "smartflash.jp",
    "real-int.jp",
    "money-zine.com",
    "money1.jp",
}

EXCLUDE_DOMAINS = VIDEO_DOMAINS | PAYWALL_DOMAINS | TABLOID_DOMAINS

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


def build_url(query: str, when: str = "1d") -> str:
    q = f"{query} when:{when} {EXCLUDE_QUERY}"
    return (
        "https://news.google.com/rss/search?q="
        + quote(q)
        + "&hl=ja&gl=JP&ceid=JP:ja"
    )


# 各カテゴリのクエリ (query, time_window) のリスト
# 経済は複数キーワードで直近48時間ぶんを取得・重複除外して件数を増やす
CATEGORY_QUERIES: dict[str, list[tuple[str, str]]] = {
    "politics":  [("日本 政治", "1d")],
    "economics": [
        ("日本 経済",        "2d"),
        ("日本 金融",        "2d"),
        ("日本 株式 市場",   "2d"),
        ("日本 景気",        "2d"),
        ("日本 為替 円",     "2d"),
        ("企業 決算 日本",   "2d"),
    ],
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


def fetch_category(name: str, queries: list[tuple[str, str]]) -> list[dict]:
    """カテゴリ毎の複数クエリを取得して link で重複排除する。"""
    seen_links: set[str] = set()
    merged: list[dict] = []
    for query, when in queries:
        url = build_url(query, when)
        print(f"[{name}] fetching ({query}, when:{when})")
        try:
            xml = fetch(url)
            items = parse(xml)
        except (urllib.error.URLError, ET.ParseError) as err:
            print(f"  ERROR: {err}", file=sys.stderr)
            continue
        before = len(items)
        items = [i for i in items if is_article(i)]
        added = 0
        for item in items:
            link = item.get("link", "")
            if not link or link in seen_links:
                continue
            seen_links.add(link)
            merged.append(item)
            added += 1
        print(f"  {added} new / {len(items)} filtered / {before} raw")
    merged.sort(key=lambda i: i.get("pubTimestamp", 0), reverse=True)
    return merged


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fetched_at = dt.datetime.now(dt.timezone.utc).isoformat()
    failures = 0

    for name, queries in CATEGORY_QUERIES.items():
        items = fetch_category(name, queries)
        if not items:
            failures += 1
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

    # 生成AIカテゴリ（別ロジック）
    print("[ai] fetching generative-AI feeds")
    try:
        ai_items = fetch_ai_articles(hours=72)
    except Exception as err:  # noqa: BLE001
        print(f"  ERROR: {err}", file=sys.stderr)
        failures += 1
    else:
        (OUT_DIR / "ai.json").write_text(
            json.dumps(
                {"fetched_at": fetched_at, "items": ai_items},
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"  wrote ai.json ({len(ai_items)} items)")

    total = len(CATEGORY_QUERIES) + 1
    return 1 if failures == total else 0


# =====================================================================
# 生成AIニュース（ai-news-digest と同じソース）
# =====================================================================

AI_FEEDS = [
    ("Anthropic",     "https://www.anthropic.com/news/rss.xml"),
    ("OpenAI",        "https://openai.com/blog/rss.xml"),
    ("Google AI",     "https://blog.google/technology/ai/rss/"),
    ("Hugging Face",  "https://huggingface.co/blog/feed.xml"),
    ("MIT News (AI)", "https://news.mit.edu/topic/mitartificial-intelligence2-rss.xml"),
    ("arXiv cs.AI",   "https://export.arxiv.org/rss/cs.AI"),
    ("ITmedia AI+",   "https://rss.itmedia.co.jp/rss/2.0/aiplus.xml"),
]

AI_SOURCE_PRIORITY = {
    "Anthropic":     5,
    "OpenAI":        5,
    "Google AI":     4,
    "ITmedia AI+":   4,
    "Hugging Face":  3,
    "Ledge.ai":      3,
    "MIT News (AI)": 2,
    "arXiv cs.AI":   1,
}

AI_JA_SOURCES = {"ITmedia AI+", "Ledge.ai"}
AI_MAX_PER_SOURCE = 2
AI_TOP_N = 16


def _ai_translate(text: str, _cache: dict = {}) -> str:
    if not text:
        return ""
    if text in _cache:
        return _cache[text]
    try:
        from deep_translator import GoogleTranslator
        result = GoogleTranslator(source="auto", target="ja").translate(text[:4500])
        _cache[text] = result or text
        return _cache[text]
    except Exception as err:  # noqa: BLE001
        print(f"  translate failed: {err}", file=sys.stderr)
        return text


def fetch_ai_articles(hours: int) -> list[dict]:
    try:
        import feedparser
    except ImportError:
        print("  feedparser is not installed; skipping AI feeds", file=sys.stderr)
        return []

    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours)
    raw: list[dict] = []

    for source, url in AI_FEEDS:
        try:
            feed = feedparser.parse(url)
            count = 0
            for entry in feed.entries:
                parsed = entry.get("published_parsed") or entry.get("updated_parsed")
                if not parsed:
                    continue
                published = dt.datetime(*parsed[:6], tzinfo=dt.timezone.utc)
                if published < cutoff:
                    continue
                raw.append({
                    "source":    source,
                    "title":     (entry.get("title") or "").strip(),
                    "link":      (entry.get("link") or "").strip(),
                    "published": published,
                })
                count += 1
            print(f"  [{source}] {count} new entries")
        except Exception as err:  # noqa: BLE001
            print(f"  [{source}] ERROR: {err}", file=sys.stderr)

    raw.extend(_fetch_ledgeai(cutoff))

    # 優先度＋新しい順
    raw.sort(
        key=lambda x: (AI_SOURCE_PRIORITY.get(x["source"], 1), x["published"]),
        reverse=True,
    )

    # ソースごとに上限を設けて多様性を確保
    per_source: dict[str, int] = {}
    selected: list[dict] = []
    for a in raw:
        s = a["source"]
        if per_source.get(s, 0) >= AI_MAX_PER_SOURCE:
            continue
        per_source[s] = per_source.get(s, 0) + 1
        selected.append(a)
        if len(selected) >= AI_TOP_N:
            break

    # 表示用に整形（必要なら日本語化）
    result: list[dict] = []
    for a in selected:
        title_orig = a["title"]
        title_ja = title_orig if a["source"] in AI_JA_SOURCES else _ai_translate(title_orig)
        pub = a["published"]
        result.append({
            "title":        title_ja,
            "titleOriginal": title_orig if title_orig != title_ja else "",
            "link":         a["link"],
            "pubDate":      pub.strftime("%a, %d %b %Y %H:%M:%S +0000"),
            "pubTimestamp": pub.timestamp(),
            "sourceName":   a["source"],
        })
    # 最終的に新しい順
    result.sort(key=lambda i: i.get("pubTimestamp", 0), reverse=True)
    return result


def _fetch_ledgeai(cutoff: dt.datetime) -> list[dict]:
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        return []
    try:
        resp = requests.get(
            "https://ledge.ai/",
            timeout=10,
            headers={"User-Agent": USER_AGENT},
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        items: list[dict] = []
        seen: set[str] = set()
        now = dt.datetime.now(dt.timezone.utc)
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if "/articles/" not in href:
                continue
            link = href if href.startswith("http") else f"https://ledge.ai{href}"
            if link in seen:
                continue
            seen.add(link)
            title = a_tag.get_text(strip=True)
            if not title:
                continue
            items.append({
                "source":    "Ledge.ai",
                "title":     title,
                "link":      link,
                "published": now,
            })
        print(f"  [Ledge.ai] {len(items)} entries (scraped)")
        return items[:20]
    except Exception as err:  # noqa: BLE001
        print(f"  [Ledge.ai] ERROR: {err}", file=sys.stderr)
        return []


if __name__ == "__main__":
    sys.exit(main())
