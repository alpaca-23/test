# ai-news-digest

主要な生成AI関連メディアの RSS / Web を集約し、日本語要約付きのトップニュースをメールで配信するツールです。

## 配信ソース

| ソース | 取得方法 | 優先度 |
| --- | --- | --- |
| Anthropic | RSS | ★★★★★ |
| OpenAI | RSS | ★★★★★ |
| Google AI | RSS | ★★★★ |
| ITmedia AI+ | RSS | ★★★★ |
| Hugging Face | RSS | ★★★ |
| Ledge.ai | スクレイピング | ★★★ |
| MIT News (AI) | RSS | ★★ |
| arXiv cs.AI | RSS | ★ |

## 記事の選び方

1. ソース優先度 → 高い順
2. 公開日時 → 新しい順
3. **1ソースあたり最大2件**に制限して多様性を確保
4. 合計 **トップ10件** を配信

## 日本語要約

- **日本語ソース**（ITmedia・Ledge.ai）: そのまま表示
- **英語ソース**: `deep-translator`（Google 翻訳）で日本語に翻訳

## セットアップ

```powershell
cd ai-news-digest
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
cp .env.example .env   # SMTP 認証情報と宛先を編集
```

### iCloud から送信する場合（推奨）

1. Apple ID で **2ファクタ認証** を有効化（必須）
2. <https://account.apple.com/account/manage> → 「サインインとセキュリティ」→ **「App用パスワード」** を生成
3. `.env` を以下のように設定:

   ```env
   SMTP_HOST=smtp.mail.me.com
   SMTP_PORT=587
   SMTP_USER=you@icloud.com
   SMTP_PASSWORD=abcd-efgh-ijkl-mnop   # App用パスワード
   MAIL_FROM=you@icloud.com
   MAIL_TO=you@icloud.com
   ```

## 動作確認（送信せず HTML を標準出力）

```powershell
$env:DRY_RUN=1; .\.venv\Scripts\python main.py
```

## 手動実行

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\run.ps1
```

## 定期実行（Windows タスクスケジューラ）

`run.ps1` がタスクスケジューラから呼び出されます。  
登録済みタスク: **毎日 08:00 / 19:00** に自動実行。

タスクを再登録する場合:

```powershell
$script = "$PWD\run.ps1"
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$script`""
$trigger08 = New-ScheduledTaskTrigger -Daily -At "08:00"
$trigger19 = New-ScheduledTaskTrigger -Daily -At "19:00"
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
Register-ScheduledTask -TaskName "AI-News-Digest-Morning" -Action $action -Trigger $trigger08 -Settings $settings -Principal $principal -Force
Register-ScheduledTask -TaskName "AI-News-Digest-Evening" -Action $action -Trigger $trigger19 -Settings $settings -Principal $principal -Force
```

## 設定

| 環境変数 | 説明 | 既定値 |
| --- | --- | --- |
| `SMTP_HOST` | SMTP サーバー | — |
| `SMTP_PORT` | SMTP ポート | `587` |
| `SMTP_USER` | SMTP ユーザー名 | — |
| `SMTP_PASSWORD` | SMTP パスワード（App用） | — |
| `MAIL_FROM` | 送信元アドレス | `SMTP_USER` と同じ |
| `MAIL_TO` | 送信先アドレス（カンマ区切り可） | — |
| `LOOKBACK_HOURS` | 何時間前までの記事を対象とするか | `24` |
| `DRY_RUN` | `1` の場合は送信せず HTML を標準出力 | — |

## 配信ソースの追加

`main.py` の `FEEDS` リストに `(表示名, RSS URL)` を追加し、`SOURCE_PRIORITY` に優先度を設定するだけで拡張できます。
