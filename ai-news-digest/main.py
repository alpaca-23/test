"""AI news digest: fetch latest generative-AI articles and email a digest."""
from __future__ import annotations

import os
import smtplib
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Iterable

import feedparser

FEEDS: list[tuple[str, str]] = [
    ("Anthropic", "https://www.anthropic.com/news/rss.xml"),
    ("OpenAI", "https://openai.com/blog/rss.xml"),
    ("Google AI", "https://blog.google/technology/ai/rss/"),
    ("Hugging Face", "https://huggingface.co/blog/feed.xml"),
    ("MIT News (AI)", "https://news.mit.edu/topic/mitartificial-intelligence2-rss.xml"),
    ("arXiv cs.AI", "https://export.arxiv.org/rss/cs.AI"),
]


@dataclass(frozen=True)
class Article:
    source: str
    title: str
    link: str
    summary: str
    published: datetime


def _parse_published(entry) -> datetime | None:
    for key in ("published_parsed", "updated_parsed"):
        value = entry.get(key)
        if value:
            return datetime(*value[:6], tzinfo=timezone.utc)
    return None


def fetch_recent(hours: int) -> list[Article]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    articles: list[Article] = []
    for source, url in FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            published = _parse_published(entry)
            if not published or published < cutoff:
                continue
            articles.append(
                Article(
                    source=source,
                    title=entry.get("title", "(no title)").strip(),
                    link=entry.get("link", "").strip(),
                    summary=(entry.get("summary", "") or "").strip(),
                    published=published,
                )
            )
    articles.sort(key=lambda a: a.published, reverse=True)
    return articles


def render_html(articles: Iterable[Article], hours: int) -> str:
    articles = list(articles)
    if not articles:
        body = f"<p>過去 {hours} 時間に新しい記事は見つかりませんでした。</p>"
    else:
        items = "".join(
            f'<li style="margin-bottom:12px;">'
            f'<div><a href="{a.link}"><strong>{a.title}</strong></a></div>'
            f'<div style="color:#666;font-size:12px;">'
            f'{a.source} · {a.published.strftime("%Y-%m-%d %H:%M UTC")}'
            f"</div>"
            f"</li>"
            for a in articles
        )
        body = f"<ul style=\"padding-left:18px;\">{items}</ul>"
    return (
        '<div style="font-family:-apple-system,Helvetica,Arial,sans-serif;'
        'max-width:680px;margin:auto;">'
        f"<h2>最新の生成AIニュース ({len(articles)} 件)</h2>"
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
    articles = fetch_recent(hours)
    html = render_html(articles, hours)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    subject = f"[AI Digest] {today} - {len(articles)} 件"

    if os.environ.get("DRY_RUN") == "1":
        sys.stdout.write(html + "\n")
        return 0

    send_email(html, subject)
    print(f"Sent digest with {len(articles)} articles.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
