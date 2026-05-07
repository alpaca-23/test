# new-page — 新しいページを追加する

引数で指定されたページ名・種別に基づいて、日本語ページ（と必要に応じて英語版）を作成する。

## 使い方

```
/new-page <ページ種別> <ページ名>
```

例:
- `/new-page tanpin 太白とろろ（250g）`
- `/new-page setsumeikai お歳暮特集`

## ページ種別と対応するテンプレート構造

### tanpin（単品商品詳細ページ）
- 使用CSS: `css/shopping.css`
- 参考: `tanpin-60g.html`, `tanpin-180g.html`, `tanpin-35g.html`
- 構成: topbar → header → hero → breadcrumb → page-body（sidebar + 商品詳細）→ footer

### osusume-item（おすすめ商品カード追加）
- `osusume.html` の `product-grid` に `<article class="product-card">` を追加する
- 同時に `en/products.html` にも英語版カードを追加する

### info（情報ページ）
- 使用CSS: `css/about.css`（または新規CSSを作成）
- 参考: `about.html`, `company.html`

## 作成手順

1. ユーザーに必要情報を確認する（商品名、価格、説明文、使用する画像ファイル名）
2. 既存の類似ページを参考に新ページを作成する
3. `sitemap.xml` に新ページを追加する（存在する場合）
4. 必要に応じて英語版も作成する
5. 作成後 `/deploy` で公開するか確認する
