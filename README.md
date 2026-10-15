# Aspire MCP

> ## 🚧 Status: IN DEVELOPMENT
> Early prototype. The live bridge into Aspire has **not yet been tested against a real Aspire install**; expect breakage.
> **Using an AI to install it?** Point it at [INSTALL_FOR_AI.md](INSTALL_FOR_AI.md), and send me the output of the `feedback_report` tool.

> Unofficial. Not affiliated with Vectric. Requires your own licensed Aspire. This repo contains no Vectric software or data.

## Install (Windows PC with Aspire)

Needs [uv](https://docs.astral.sh/uv/) (`winget install astral-sh.uv`). Then add to your MCP client config
(Claude Desktop `claude_desktop_config.json`, Claude Code, Cursor, etc.):

```json
{
  "mcpServers": {
    "aspire": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/NicoMancinelli/AspireMCP", "aspire-mcp"],
      "env": {
        "ASPIRE_DATA_DIR": "C:\\ProgramData\\Vectric\\Aspire\\V8.5",
        "ASPIRE_INSTALL_DIR": "C:\\Program Files\\Aspire 8.5"
      }
    }
  }
}
```

Claude Code: `claude mcp add aspire -- uvx --from git+https://github.com/NicoMancinelli/AspireMCP aspire-mcp`

The two env vars are optional (common locations are auto-detected); set them if your folders differ.
For live control, copy `mcp_bridge.lua` (from `aspire_mcp/gadgets/`) into Aspire's Gadgets folder
(e.g. `Documents\Vectric Files\Gadgets`), restart Aspire, and run it from the Gadgets menu.

MCP server (stdio, Python) for Vectric Aspire.

- **Offline tools** (no Aspire needed): post processors, toolpath defaults, fonts, clipart, tool-DB scrape, Lua API search.
  Paths come from `ASPIRE_DATA_DIR` / `ASPIRE_INSTALL_DIR` (default: sample files in `Vectric Files/`).
- **Live bridge**: copy `aspire_mcp/gadgets/mcp_bridge.lua` into Aspire's Gadgets folder and run it. It connects to
  `127.0.0.1:8765` (the MCP server listens) and executes Lua sent by `run_lua`. It blocks Aspire's UI while connected.

## Status / verified vs. not

- Verified: offline tools, TCP protocol (simulated gadget), MCP stdio smoke test (`pytest`).
- **Unverified (needs Aspire on Windows):** that gadgets can `require("socket")`; `get_job_info`, `import_vector_file`.
- Binary strings in `Aspire.exe` show an embedded LuaSocket (`socket.core`, tcp bind/connect/accept) and a luabind class table.
- `aspire_mcp/data/lua_api_catalog.json` is a *heuristic* extraction (`tools/extract_lua_api.py`); method lists may be mis-grouped.
- REA's Ghidra/Hopper/IDA providers are not configured here, so no decompilation was done, only string recovery.

## Dev

    uv venv && uv pip install -e ".[dev]" && .venv/bin/pytest
    claude/other client config: command = <repo>/.venv/bin/aspire-mcp
