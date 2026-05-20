# 大老昆布 – 株式会社明和

滋賀県彦根市のとろろ昆布専門店「大老昆布（株式会社明和）」の公式ウェブサイトです。

## サイト概要

- **店名**: 大老昆布（株式会社明和）
- **所在地**: 〒522-0000 滋賀県彦根市中薮2丁目5-8
- **電話**: 0749-23-3939 / FAX: 0749-26-2786
- **営業時間**: 平日 9:00〜17:00
- **創業**: 昭和55年（1980年）
- **URL**: https://alpaca-23.github.io/test/

## サイト構成

| ファイル | ページ名 | 内容 |
|---|---|---|
| [index.html](index.html) | TOP | トップページ・ご挨拶・おすすめ商品・お知らせ |
| [about.html](about.html) | 大老昆布のご紹介 | 創業の歴史・屋号の由来 |
| [osusume.html](osusume.html) | おすすめ商品 | 商品一覧 |
| [shopping.html](shopping.html) | ショッピング | 詰め合わせ・単品商品一覧 |
| [tanpin.html](tanpin.html) | 単品商品 | 単品商品の詳細 |
| [tanpin-35g.html](tanpin-35g.html) | 太白とろろ（35g）| 単品35g詳細ページ |
| [tanpin-60g.html](tanpin-60g.html) | 太白とろろ（60g）| 単品60g詳細ページ |
| [tanpin-180g.html](tanpin-180g.html) | 太白とろろ（180g）| 単品180g詳細ページ |
| [shopping-a2.html](shopping-a2.html) | 詰め合わせA2 | 詰め合わせ商品A2詳細 |
| [shopping-a4.html](shopping-a4.html) | 詰め合わせA4 | 詰め合わせ商品A4詳細 |
| [shopping-b2.html](shopping-b2.html) | 詰め合わせB2 | 詰め合わせ商品B2詳細 |
| [howto.html](howto.html) | お買い物方法 | 支払い・送料・返品について |
| [quantity.html](quantity.html) | 包装について | 包装見本・婚礼大小 |
| [process.html](process.html) | とろろ昆布の加工工程 | 8ステップの製造工程 |
| [company.html](company.html) | 会社案内 | 会社情報 |
| [tourism.html](tourism.html) | 彦根観光おすすめ情報 | 彦根城・夢京橋キャッスルロードなど |
| [contact.html](contact.html) | お問い合わせ | 問い合わせフォーム |
| [en/index.html](en/index.html) | English | 英語版トップページ |

## 商品ラインナップ

道南白口浜産の真昆布を使用したとろろ昆布を直販しています。

- **太白とろろ（35g）** — ¥750（税込）
- **太白とろろ（60g）** — ¥1,460（税込）　※当店人気No.1
- **太白とろろ（180g）** — ¥2,720（税込）
- **詰め合わせ各種** — ギフト・贈答品向け

贈答品には各種包装紙・のし紙に対応しています。

## 注文システム

### フロー（4ステップ）

```
商品詳細ページ → cart.html → customer.html → confirm.html → complete.html
（カートに追加）  （カート確認）  （お客様情報入力）  （注文確認・送信）  （完了）
```

### STEP 1：カートに入れる（商品詳細ページ）

各商品詳細ページのフォームから商品をカートに追加する。

| フォームフィールド | 内容 |
|---|---|
| `item_cd` | 商品コード（例: A-0001） |
| `item_nm` | 商品名 |
| `price` | 単価（税込・円） |
| `housoushi` | 包装紙の種類 |
| `noshi` | のし紙の種類 |
| `qty` | 数量 |

- フォーム送信時に `cart.js` の `addToCartFromForm()` を呼び出す
- カートデータは **localStorage**（キー: `tairou_cart`）に JSON 配列で保存
- 同一商品コード＋同一包装・のしの場合は数量を加算してマージ

### STEP 2：カート確認（cart.html）

- localStorage からカートを読み込み、商品一覧・合計金額を表示
- 数量変更・削除が可能
- 「お客様情報入力へ進む」ボタンで `customer.html` へ遷移

### STEP 3：お客様情報入力（customer.html）

フォームバリデーション後、入力内容を **sessionStorage**（キー: `tairou_customer`）に保存して `confirm.html` へ遷移。

| フィールド | 必須 | 内容 |
|---|:---:|---|
| 姓名（漢字） | ✓ | 注文者氏名 |
| 姓名（フリガナ） | ✓ | |
| メールアドレス | ✓ | 確認入力あり |
| 郵便番号 | ✓ | |
| 都道府県 | ✓ | |
| 市区町村・住所 | ✓ | |
| 電話番号 | ✓ | |
| 備考 | — | のし宛名などの要望 |
| 別送先 | — | チェックで入力欄を追加表示 |

### STEP 4：注文確認・送信（confirm.html）

- localStorage（カート）と sessionStorage（お客様情報）を読み込んで確認画面を表示
- 「ご注文を確定する」ボタンで **Formspree** へ POST 送信

```
エンドポイント: https://formspree.io/f/xzdojozd
メソッド: POST
Content-Type: application/json
```

送信ペイロードに含まれる主なフィールド：

| キー | 内容 |
|---|---|
| `お名前` | 注文者氏名（漢字） |
| `フリガナ` | 注文者氏名（フリガナ） |
| `メールアドレス` | 連絡先メール |
| `郵便番号` | |
| `都道府県` | |
| `住所` | 市区町村以降 |
| `電話番号` | |
| `別送先` | 届け先が異なる場合のみ |
| `注文内容` | 商品名・包装・のし・数量・単価の一覧テキスト |
| `合計金額` | 商計（税込） |
| `要望等` | 備考欄 |

- 送信成功後：localStorage（カート）と sessionStorage（お客様情報）を削除し、`complete.html` へ遷移
- 送信失敗時：ボタンを再有効化してエラーアラートを表示

---

## お問い合わせシステム

### フォーム（contact.html）

| フィールド | 必須 | フォーム名 |
|---|:---:|---|
| 氏名 | ✓ | `氏名` |
| 住所 | — | `住所` |
| 電話番号 | — | `電話番号` |
| FAX | — | `FAX` |
| メールアドレス | ✓ | `メールアドレス` |
| お問い合わせ内容 | ✓ | `お問い合わせ内容` |

### 送信先

注文フォームと同じ Formspree エンドポイントを使用。

```
エンドポイント: https://formspree.io/f/xzdojozd
メソッド: POST
Content-Type: multipart/form-data（FormData）
```

追加ヘッダー（Formspree 制御用）：

| キー | 値 |
|---|---|
| `_subject` | `【大老昆布】お問い合わせ：{氏名}` |
| `_replyto` | 入力されたメールアドレス |
| `種別` | `お問い合わせ`（hidden） |

- 送信成功後：フォームを非表示にして成功メッセージを表示
- 直接連絡先：kk-meiwa@proof.ocn.ne.jp

---

## お支払い・配送

| 項目 | 内容 |
|---|---|
| 支払方法 | ゆうちょ銀行への**事前振込**のみ |
| 振込先 | ゆうちょ銀行：（株）明和 ／ 記号 **14690** ／ 番号 **3771751** |
| 振込手数料 | お客様負担 |
| 送料 | 注文内容確認後に弊社から連絡 |
| 発送 | 入金確認後、**営業日3日以内** |
| 返品 | 開封後は不可。弊社過失による破損は新品交換（返品送料は弊社負担） |

---

## 技術スタック

- HTML5 / CSS3（バニラ、フレームワーク不使用）
- Google Fonts（Noto Serif JP / Noto Sans JP）
- レスポンシブデザイン（モバイル対応）
- Schema.org 構造化データ（LocalBusiness）
- 日英バイリンガル対応
- フォーム送信：[Formspree](https://formspree.io/)（`xzdojozd`）
- カートデータ：localStorage（`tairou_cart`）
- 注文途中データ：sessionStorage（`tairou_customer`）
