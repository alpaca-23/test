# ai-tech-radar

生成AIの**実践・技術記事**（RAG、エージェント、プロンプト設計、事例など）を Qiita / Zenn / 企業テックブログから収集し、週次でメール配信します。
公式リリース系のニュースは姉妹プロジェクト [`ai-news-digest`](../ai-news-digest/) を参照してください。

## 収集ソース (既定)

- **Qiita** タグ: 生成AI / LLM / RAG / LangChain / ChatGPT
- **Zenn** トピック: LLM / 生成AI / RAG / AI Agent
- **企業テックブログ**: NTT Docomo Developers

ソースの追加・削除は `main.py` の `FEEDS` リストを編集してください。

## セットアップ

```bash
cd ai-tech-radar
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### iCloud SMTP の設定

1. Apple ID で **2ファクタ認証** を有効化
2. <https://account.apple.com/account/manage> → サインインとセキュリティ → **「App用パスワード」** を生成
3. `.env` を編集:

   ```env
   SMTP_HOST=smtp.mail.me.com
   SMTP_PORT=587
   SMTP_USER=you@icloud.com
   SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx
   MAIL_FROM=you@icloud.com
   MAIL_TO=you@icloud.com
   LOOKBACK_HOURS=168
   ```

`ai-news-digest` で App用パスワードを発行済みの場合は同じものを流用できます。

## 動作確認 (送信せず HTML を出力)

```bash
DRY_RUN=1 python main.py
```

## 実行

```bash
set -a && source .env && set +a
python main.py
```

## 定期実行

`.github/workflows/ai-tech-radar.yml` により **毎週月曜 JST 08:00**（直前 7 日間分）に自動配信されます。
リポジトリの **Settings → Secrets and variables → Actions** に `ai-news-digest` と同じ Secrets が設定されていれば追加作業は不要です。

## 設定

| 環境変数         | 説明                                       | 既定値 |
| ---------------- | ------------------------------------------ | ------ |
| `LOOKBACK_HOURS` | 何時間前までの記事を対象とするか           | `168` (7日) |
| `DRY_RUN`        | `1` の場合は送信せず HTML を標準出力に表示 | (未設定) |
