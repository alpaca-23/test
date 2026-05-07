# CLAUDE.md — 大老昆布 ウェブサイト開発ガイド

## プロジェクト概要

滋賀県彦根市のとろろ昆布専門店「大老昆布（株式会社明和）」の公式サイト。
HTML/CSS のみ（フレームワーク不使用）。日英バイリンガル対応。
GitHub Pages でホスティング: `https://alpaca-23.github.io/test/`

- **リポジトリ**: `https://github.com/alpaca-23/test`
- **デプロイブランチ**: `claude/modernize-website-design-1QuZK`（GitHub Pages の Source に設定済み）
- **Git remote**: SSH（`git@github.com:alpaca-23/test.git`）

---

## ディレクトリ構造

```
/
├── *.html          # 日本語ページ
├── en/             # 英語ページ（日本語と1対1対応）
├── css/            # 各ページ専用CSS（ページ名と同名）
├── images/         # 全ページ共通の画像素材
└── .claude/        # Claude Code 設定
```

---

## ページ一覧と CSS 対応

| HTMLファイル | CSSファイル | ページ名 | 英語版 |
|---|---|---|---|
| index.html | css/index.css | TOP | en/index.html |
| about.html | css/about.css | 大老昆布のご紹介 | en/about.html |
| osusume.html | css/osusume.css | おすすめ商品 | en/products.html |
| shopping.html | css/shopping.css | ショッピング（詰め合わせ・単品） | — |
| tanpin.html | css/shopping.css | 単品商品一覧 | — |
| tanpin-35g.html | css/shopping.css | 太白とろろ（35g）詳細 | — |
| tanpin-60g.html | css/shopping.css | 太白とろろ（60g）詳細 | — |
| tanpin-180g.html | css/shopping.css | 太白とろろ（180g）詳細 | — |
| shopping-a2.html | css/shopping.css | 詰め合わせA2詳細 | — |
| shopping-a4.html | css/shopping.css | 詰め合わせA4詳細 | — |
| shopping-b2.html | css/shopping.css | 詰め合わせB2詳細 | — |
| howto.html | css/howto.css | お買い物方法 | en/howto.html |
| quantity.html | css/quantity.css | 包装について | — |
| process.html | css/process.css | とろろ昆布の加工工程 | — |
| company.html | css/company.css | 会社案内 | en/company.html |
| tourism.html | css/tourism.css | 彦根観光おすすめ情報 | — |
| contact.html | css/contact.css | お問い合わせ | en/contact.html |

英語版は `../css/` で日本語版と同じ CSS を共有している。

---

## 画像素材一覧

```
images/
├── product-tairou-single.jpg   # 太白とろろ 60g（化粧筒）
├── product-tairou-180g.jpg     # 太白とろろ 180g（大容量パック）
├── product-tairou-35g.jpg      # 太白とろろ 35g（小パック）
├── product-tairou-box.jpg      # 化粧箱（汎用）
├── product-box-a.jpg           # 化粧箱詰め合わせ A
├── product-tororo-featured.jpg # とろろ昆布フィーチャー画像
├── konbu-diagram.jpg           # 昆布説明図
├── set-a2-two-containers.jpg   # 詰め合わせA2（筒×2）
├── set-a4-konbu-candy.jpg      # 詰め合わせA4
├── set-b2-three-containers.jpg # 詰め合わせB2（筒×3）
├── packaging-*.jpg             # 包装紙サンプル各種
├── process-*.jpg/png           # 加工工程イラスト（8ステップ）
└── tourism-*.jpg               # 彦根観光写真
```

英語版から参照する際は `../images/` と書く。

---

## 商品ラインナップ

| 商品名 | 画像ファイル | 価格（税込）|
|---|---|---|
| 太白とろろ（35g） | product-tairou-35g.jpg | ¥750 |
| 太白とろろ（60g） | product-tairou-single.jpg | ¥1,460 |
| 太白とろろ（180g） | product-tairou-180g.jpg | ¥2,720 |
| 化粧箱詰め合わせ A | product-box-a.jpg | 要問い合わせ |

---

## 開発ルール

### HTML
- 各ページは `<div class="topbar">` → `<header>` → メインコンテンツ → `<footer>` の構造
- 言語切替リンクは topbar 内に `<div class="lang-switch">` で配置
- 日本語ページ: `<html lang="ja">` / 英語ページ: `<html lang="en">`
- 商品画像は `<img>` タグを使用（絵文字プレースホルダーは使わない）

### CSS
- CSS は各ページごとに `css/` 以下に専用ファイルを置く
- ページ間で共通のデザイントークン（色・フォント）は各 CSS ファイルに `:root` で定義
- 主な色変数: `--green-deep`, `--green-mid`, `--green-light`, `--warm-bg`, `--text-main`

### 日英対応
- 日本語ページを正とし、英語ページを対応させる
- 英語ページでは `../css/` `../images/` で日本語ページの CSS・画像を共有する
- 英語ページに存在しないページ（tanpin, process, quantity, tourism 等）は日本語ページにリンクする際に `(Japanese page)` と明示する

### デプロイ
- 作業ブランチ: `claude/modernize-website-design-1QuZK`
- 変更後は必ずコミット & プッシュ（`git push origin claude/modernize-website-design-1QuZK`）
- GitHub Pages は上記ブランチを Source として自動デプロイ

---

## よく使うコマンド

```bash
# 変更をプッシュ（デプロイ）
git add -p && git commit -m "..." && git push origin claude/modernize-website-design-1QuZK

# 英語版と日本語版の画像差分を確認
grep -n 'src="images/' osusume.html
grep -n 'src="../images/' en/products.html

# ローカルプレビュー
python3 -m http.server 8080
# → http://localhost:8080/osusume.html
```
