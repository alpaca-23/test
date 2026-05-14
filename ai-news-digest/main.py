"""AI news digest: fetch latest generative-AI articles and email a digest."""
from __future__ import annotations

import os
import smtplib
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import unescape
from re import sub

import feedparser
import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

FEEDS: list[tuple[str, str]] = [
    ("Anthropic", "https://www.anthropic.com/news/rss.xml"),
    ("OpenAI", "https://openai.com/blog/rss.xml"),
    ("Google AI", "https://blog.google/technology/ai/rss/"),
    ("Hugging Face", "https://huggingface.co/blog/feed.xml"),
    ("MIT News (AI)", "https://news.mit.edu/topic/mitartificial-intelligence2-rss.xml"),
    ("arXiv cs.AI", "https://export.arxiv.org/rss/cs.AI"),
    ("ITmedia AI+", "https://rss.itmedia.co.jp/rss/2.0/aiplus.xml"),
]

# Sources whose content is already in Japanese (skip translation)
JA_SOURCES = {"ITmedia AI+", "Ledge.ai"}

TOP_N = 10

# Priority weight per source for ranking (higher = more important)
SOURCE_PRIORITY: dict[str, int] = {
    "Anthropic": 5,
    "OpenAI": 5,
    "Google AI": 4,
    "Hugging Face": 3,
    "ITmedia AI+": 4,
    "Ledge.ai": 3,
    "MIT News (AI)": 2,
    "arXiv cs.AI": 1,
}


@dataclass(frozen=True)
class Article:
    source: str
    title: str
    link: str
    summary: str
    published: datetime


def _strip_html(text: str) -> str:
    return unescape(sub(r"<[^>]+>", " ", text)).strip()


def _parse_published(entry) -> datetime | None:
    for key in ("published_parsed", "updated_parsed"):
        value = entry.get(key)
        if value:
            return datetime(*value[:6], tzinfo=timezone.utc)
    return None


def fetch_rss(hours: int) -> list[Article]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    articles: list[Article] = []
    for source, url in FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                published = _parse_published(entry)
                if not published or published < cutoff:
                    continue
                articles.append(Article(
                    source=source,
                    title=entry.get("title", "").strip(),
                    link=entry.get("link", "").strip(),
                    summary=_strip_html(entry.get("summary", "") or ""),
                    published=published,
                ))
        except Exception:
            pass
    return articles


def fetch_ledgeai() -> list[Article]:
    try:
        resp = requests.get(
            "https://ledge.ai/",
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        articles: list[Article] = []
        seen: set[str] = set()
        for a_tag in soup.find_all("a", href=True):
            href: str = a_tag["href"]
            if "/articles/" not in href:
                continue
            link = href if href.startswith("http") else f"https://ledge.ai{href}"
            if link in seen:
                continue
            seen.add(link)
            title = a_tag.get_text(strip=True)
            if not title:
                continue
            articles.append(Article(
                source="Ledge.ai",
                title=title,
                link=link,
                summary="",
                published=datetime.now(timezone.utc),
            ))
        return articles[:20]
    except Exception:
        return []


def _score(article: Article) -> tuple[int, datetime]:
    return (SOURCE_PRIORITY.get(article.source, 1), article.published)


def fetch_and_rank(hours: int) -> list[Article]:
    articles = fetch_rss(hours) + fetch_ledgeai()
    articles.sort(key=_score, reverse=True)
    return articles[:TOP_N * 3]  # keep buffer for dedup/filter


def _translate(text: str) -> str:
    if not text:
        return ""
    try:
        return GoogleTranslator(source="auto", target="ja").translate(text[:4500])
    except Exception:
        return text


def build_summaries(articles: list[Article]) -> list[dict]:
    top = articles[:TOP_N]
    result = []
    for a in top:
        if a.source in JA_SOURCES:
            title_ja = a.title
            summary_ja = a.summary[:200] if a.summary else ""
        else:
            title_ja = _translate(a.title)
            raw = a.summary[:300] if a.summary else a.title
            summary_ja = _translate(raw)
        result.append({
            "source": a.source,
            "title_orig": a.title,
            "title_ja": title_ja,
            "link": a.link,
            "summary_ja": summary_ja,
            "published": a.published,
        })
    return result


def render_html(items: list[dict]) -> str:
    if not items:
        body = "<p>新しい記事は見つかりませんでした。</p>"
    else:
        cards = "".join(
            '<li style="margin-bottom:20px;padding-bottom:16px;border-bottom:1px solid #eee;">'
            f'<div><a href="{item["link"]}" style="font-size:16px;font-weight:bold;'
            f'color:#1a0dab;text-decoration:none;">{item["title_ja"]}</a></div>'
            f'<div style="color:#888;font-size:12px;margin:4px 0;">'
            f'{item["source"]} &middot; {item["published"].strftime("%Y-%m-%d %H:%M UTC")}'
            f' &middot; <a href="{item["link"]}" style="color:#888;">記事を読む</a></div>'
            f'<div style="color:#333;font-size:14px;margin-top:6px;line-height:1.6;">'
            f'{item["summary_ja"]}</div>'
            "</li>"
            for item in items
        )
        body = f'<ul style="padding-left:0;list-style:none;">{cards}</ul>'
    return (
        '<div style="font-family:-apple-system,Helvetica,Arial,sans-serif;max-width:680px;margin:auto;">'
        f'<h2 style="border-bottom:2px solid #333;padding-bottom:8px;">'
        f'本日のAIトップニュース（{len(items)}件）</h2>'
        f"{body}"
        "</div>"
    )


def send_email(html: str, subject: str) -> None:
    host = os.environ["SMTP_HOST"]
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ["SMTP_USER"]
    password = os.environ["SMTP_PASSWORD"]
    sender = os.environ.get("MAIL_FROM", user)
    recipients = [r.strip() for r in os.environ["MAIL_TO"].split(",") if r.strip()]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.sendmail(sender, recipients, msg.as_string())


def main() -> int:
    hours = int(os.environ.get("LOOKBACK_HOURS", "24"))
    articles = fetch_and_rank(hours)
    items = build_summaries(articles)
    html = render_html(items)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    subject = f"[AI Digest] {today} - トップ{len(items)}件"

    if os.environ.get("DRY_RUN") == "1":
        sys.stdout.write(html + "\n")
        return 0

    send_email(html, subject)
    print(f"Sent digest with {len(items)} articles.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
