# ai-news-digest

主要な生成AI関連メディア (Anthropic / OpenAI / Google AI / Hugging Face / MIT News / arXiv cs.AI) の RSS を集約し、直近の新着記事をメールで配信します。

## セットアップ

```bash
cd ai-news-digest
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # SMTP の認証情報と宛先を編集
```

Gmail を使う場合は [App Password](https://myaccount.google.com/apppasswords) を発行し `SMTP_PASSWORD` に設定してください。

## 動作確認 (送信せず HTML を標準出力)

```bash
DRY_RUN=1 python main.py
```

## 実行

```bash
set -a && source .env && set +a
python main.py
```

## 定期実行

### GitHub Actions

このリポジトリには `.github/workflows/ai-news-digest.yml` が含まれており、毎日 UTC 23:00 (JST 08:00) に自動配信します。
リポジトリの **Settings → Secrets and variables → Actions** に以下を登録してください。

- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`
- `MAIL_FROM`, `MAIL_TO`

### cron (自前サーバ)

```cron
0 8 * * * cd /path/to/ai-news-digest && set -a && . ./.env && set +a && /usr/bin/python3 main.py
```

## 設定

| 環境変数         | 説明                                       | 既定値 |
| ---------------- | ------------------------------------------ | ------ |
| `LOOKBACK_HOURS` | 何時間前までの記事を対象とするか           | `24`   |
| `DRY_RUN`        | `1` の場合は送信せず HTML を標準出力に表示 | (未設定) |

## 配信ソースの追加

`main.py` の `FEEDS` リストに `(表示名, RSS URL)` を追加するだけで取得対象を拡張できます。
