# 朝夕ニュース

政治・経済のニュースを朝刊・夕刊形式で届けるシンプルなウェブアプリです。

## 特徴

- **朝刊 / 夕刊**: 現在時刻から自動判定（5:00–14:00 は朝刊、それ以外は夕刊）。手動切り替えも可能。
- **政治 / 経済** の2カテゴリをタブで切り替え。
- Google ニュースの検索ベース RSS（複数の無料媒体から集約）を **GitHub Actions のビルド時に取得**し、静的 JSON として配信。
- ブラウザ側は静的 JSON を読むだけなので、CORS プロキシ不要・確実に動く。
- スケジュール実行（毎日 JST 5:00 / 14:00）と手動トリガで自動更新。

## 使い方

ローカルで開く場合は、`news-app` ディレクトリで簡易サーバーを起動してください。

```sh
cd news-app
python3 -m http.server 8000
```

ブラウザで <http://localhost:8000> を開きます。

> ※ `file://` から直接開くと一部ブラウザで `fetch` が失敗します。HTTP サーバー経由で開いてください。

## ファイル構成

- `index.html` — マークアップ
- `styles.css` — スタイル
- `app.js` — JSON 読み込み・描画・状態管理
- `fetch_news.py` — RSS を取得して `data/*.json` を生成（CI で実行）
- `data/politics.json`, `data/economics.json` — ビルド時に上書きされる記事データ

## データソース

Google ニュース RSS の検索クエリを利用しています:

- 政治: `https://news.google.com/rss/search?q=日本+政治+when:2d&hl=ja&gl=JP&ceid=JP:ja`
- 経済: `https://news.google.com/rss/search?q=日本+経済+when:2d&hl=ja&gl=JP&ceid=JP:ja`

各記事のリンク先は元の媒体（共同通信、産経、朝日、日経電子版の無料部分など）へ飛び、いずれも無料で閲覧可能です。
