# ai-news-digest

主要な生成AI関連メディア (Anthropic / OpenAI / Google AI / Hugging Face / MIT News / arXiv cs.AI) の RSS を集約し、直近の新着記事をメールで配信します。

## セットアップ

```bash
cd ai-news-digest
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # SMTP の認証情報と宛先を編集
```

### iCloud から送信する場合 (推奨設定)

1. Apple ID で **2ファクタ認証** を有効化（必須）
2. <https://account.apple.com/account/manage> → 「サインインとセキュリティ」→ **「App用パスワード」** を生成（例: `abcd-efgh-ijkl-mnop`）
3. `.env` を以下のように設定:

   ```env
   SMTP_HOST=smtp.mail.me.com
   SMTP_PORT=587
   SMTP_USER=you@icloud.com
   SMTP_PASSWORD=abcd-efgh-ijkl-mnop   # App用パスワード（Apple IDのパスワードではない）
   MAIL_FROM=you@icloud.com            # @icloud.com / @me.com / @mac.com のみ
   MAIL_TO=you@icloud.com
   ```

   注意: `MAIL_FROM` は `SMTP_USER` と同じドメイン (`@icloud.com` / `@me.com` / `@mac.com`) の自分のアドレスである必要があります。エイリアスや別ドメインは使えません。

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

| Secret 名       | iCloud の例                |
| --------------- | -------------------------- |
| `SMTP_HOST`     | `smtp.mail.me.com`         |
| `SMTP_PORT`     | `587`                      |
| `SMTP_USER`     | `you@icloud.com`           |
| `SMTP_PASSWORD` | App用パスワード            |
| `MAIL_FROM`     | `you@icloud.com`           |
| `MAIL_TO`       | `you@icloud.com`           |

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
