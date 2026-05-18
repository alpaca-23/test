# MCP Sample Server (TypeScript)

`@modelcontextprotocol/sdk`を使ったTypeScript版のサンプルMCPサーバです。

## セットアップ

```bash
cd typescript
npm install
npm run build
```

## 実行

```bash
npm start
```

開発モード(MCP Inspector付き)で起動する場合:

```bash
npx @modelcontextprotocol/inspector node build/server.js
```

## 提供する機能

### Tools
- `add(a, b)` - 2つの数値を加算
- `greet(name)` - 挨拶メッセージを返す

### Resources
- `config://app` - 静的なアプリ設定
- `greeting://{name}` - 動的な挨拶リソース(テンプレート)

## Claude Desktopへの登録

`claude_desktop_config.json` に以下を追加:

```json
{
  "mcpServers": {
    "sample-typescript": {
      "command": "node",
      "args": ["/absolute/path/to/typescript/build/server.js"]
    }
  }
}
```
