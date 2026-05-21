# 朝夕ニュース

政治・経済のニュースを朝刊・夕刊形式で届けるシンプルなウェブアプリです。

## 特徴

- **朝刊 / 夕刊**: 現在時刻から自動判定（5:00–14:00 は朝刊、それ以外は夕刊）。手動切り替えも可能。
- **政治 / 経済** の2カテゴリをタブで切り替え。
- Yahoo!ニュースの RSS フィード（無料記事）を `api.rss2json.com`（CORS 対応の公開プロキシ）経由で取得。
- ビルド不要の静的サイト（HTML / CSS / JS のみ）。

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
- `app.js` — フィード取得・描画・状態管理

## データソース

- 政治: <https://news.yahoo.co.jp/rss/topics/politics.xml>
- 経済: <https://news.yahoo.co.jp/rss/topics/business.xml>

いずれも Yahoo!ニュースの無料公開記事です。
