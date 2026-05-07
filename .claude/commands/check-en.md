# check-en — 英語版と日本語版の整合性チェック

日本語版と英語版のページを比較し、英語版に反映されていない変更や差分を洗い出して報告する。

## チェック項目

### 1. 商品画像の整合性
- `osusume.html` と `en/products.html` で使われている `<img src=` を比較する
- 絵文字（🫙 🎁 など）が残っていないか確認する
- `en/` 内のパスが `../images/` になっているか確認する

### 2. 存在するページの対応確認
以下のペアが揃っているかチェックする:
- index.html ↔ en/index.html
- about.html ↔ en/about.html
- osusume.html ↔ en/products.html
- howto.html ↔ en/howto.html
- company.html ↔ en/company.html
- contact.html ↔ en/contact.html

### 3. 英語版にない日本語ページのリンク
- `en/about.html` から `process.html` へのリンクに `(Japanese page)` の注記があるか確認する

### 4. CSS・フォントの参照
- 英語版が `../css/` で正しくCSSを参照しているか確認する

## 出力形式

チェック結果を以下の形式でまとめる:
- ✅ 問題なし
- ⚠️ 要確認
- ❌ 修正が必要

差分がある場合は修正するかどうかユーザーに確認する。
