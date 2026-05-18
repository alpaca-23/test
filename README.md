# MCP Server Practice

MCP (Model Context Protocol) サーバ構築の練習用リポジトリです。

PythonとTypeScript両方のサンプルMCPサーバを含みます。両者は同じ機能(ツールとリソース)を提供しており、実装方法の比較に使えます。

## ディレクトリ構成

- [`python/`](./python) - Python (FastMCP) によるサンプル
- [`typescript/`](./typescript) - TypeScript (`@modelcontextprotocol/sdk`) によるサンプル

## 共通の提供機能

### Tools
- `add(a, b)` - 2つの数値を加算
- `greet(name)` - 挨拶メッセージを返す

### Resources
- `config://app` - 静的なアプリ設定
- `greeting://{name}` - 動的な挨拶リソース

## 参考

- [MCP公式ドキュメント](https://modelcontextprotocol.io/)
- [Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
