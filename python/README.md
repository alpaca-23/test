# MCP Sample Server (Python)

FastMCPを使ったPython版のサンプルMCPサーバです。

## セットアップ

```bash
cd python
uv venv
source .venv/bin/activate
uv pip install -e .
```

または pip を使う場合:

```bash
pip install "mcp[cli]"
```

## 実行

```bash
python server.py
```

開発モード(MCP Inspector付き)で起動する場合:

```bash
mcp dev server.py
```

## 提供する機能

### Tools
- `add(a, b)` - 2つの数値を加算
- `greet(name)` - 挨拶メッセージを返す

### Resources
- `config://app` - 静的なアプリ設定
- `greeting://{name}` - 動的な挨拶リソース

## Claude Desktopへの登録

`claude_desktop_config.json` に以下を追加:

```json
{
  "mcpServers": {
    "sample-python": {
      "command": "python",
      "args": ["/absolute/path/to/python/server.py"]
    }
  }
}
```
