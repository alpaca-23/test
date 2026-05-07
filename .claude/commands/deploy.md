# deploy — 変更をGitHub Pagesに公開する

変更されたファイルをコミットして `claude/modernize-website-design-1QuZK` ブランチにプッシュし、GitHub Pages に反映させる。

## 手順

1. `git status` で変更ファイルを確認する
2. 変更内容をユーザーに要約して伝える
3. 変更されたファイルを `git add` でステージする（`.env` などの機密ファイルは除外）
4. 内容を表す日本語のコミットメッセージを作成し `git commit` する
5. `git push origin claude/modernize-website-design-1QuZK` でプッシュする
6. プッシュ後、GitHub Pages の URL を伝える: `https://alpaca-23.github.io/test/`

## 注意事項

- コミットメッセージは変更内容を明確に表す日本語で書く
- 画像・CSS・HTMLすべての変更を含める
- プッシュ後、GitHub Pages への反映には数分かかる場合がある
