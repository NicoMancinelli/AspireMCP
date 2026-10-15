# Install instructions for an AI assistant

You are installing **Aspire MCP** (status: **in development**, unverified against real Aspire) on a Windows PC
that has Vectric Aspire installed. Follow these steps, tell the user each result, and finish by producing
the feedback report. Do not modify anything under Aspire's install folder except adding the gadget file the user approves.

## 1. Preconditions
1. Confirm Windows and that Aspire is installed. Find the folders:
   - Install dir (contains `Aspire.exe`, `Fonts`, `Clipart`, `ProductInfo.ini`): usually `C:\Program Files\Aspire 8.5` (or newer version name).
   - Data dir (contains `PostP`, `ToolDatabase`, `Gadgets`): usually `C:\ProgramData\Vectric\Aspire\V8.5` or `...\Public\Documents\Vectric Files`.
   - Gadgets dir: `Documents\Vectric Files\Gadgets` (or `<data dir>\Gadgets`). Ask the user if unsure; search `*.lua` gadget examples like `DXF_Batch_Processor.lua`.
2. Check `uv --version`. If missing: `winget install astral-sh.uv`, then reopen the terminal.
   (User-level install; no admin rights needed.)

## 2. Register the MCP server
Use the user's client. Command is always `uvx --from git+https://github.com/NicoMancinelli/AspireMCP aspire-mcp`.
- Claude Code: `claude mcp add aspire -e ASPIRE_DATA_DIR="<data dir>" -e ASPIRE_INSTALL_DIR="<install dir>" -- uvx --from git+https://github.com/NicoMancinelli/AspireMCP aspire-mcp`
- Claude Desktop / Cursor / others: add to the client's MCP JSON config:
  `{"mcpServers":{"aspire":{"command":"uvx","args":["--from","git+https://github.com/NicoMancinelli/AspireMCP","aspire-mcp"],"env":{"ASPIRE_DATA_DIR":"<data dir>","ASPIRE_INSTALL_DIR":"<install dir>"}}}}`
  (escape backslashes in JSON). Then ask the user to restart the client.
Env vars are optional if the folders are in the usual place, but set them if you found them.

## 3. Install the bridge gadget
Download `https://raw.githubusercontent.com/NicoMancinelli/AspireMCP/main/aspire_mcp/gadgets/mcp_bridge.lua`
into the Gadgets dir. Ask the user to restart Aspire, open a job, and run "mcp_bridge" from the Gadgets menu.
Note: while running it blocks Aspire's UI; that is expected. The MCP server must be running first
(it listens on 127.0.0.1:8765). If port 8765 is taken, tell the user; this is not yet configurable.

## 4. Verify (run these MCP tools in order and record results)
1. `product_info`  -> expect product_name "Aspire" and a version.
2. `list_postprocessors`, `list_fonts`, `list_clipart` -> non-empty. If empty, the dirs are wrong; fix env vars.
3. `search_lua_api` with "CreateProfilingToolpath" -> a ToolpathManager hit.
4. `bridge_status` (with the gadget running) -> `connected: true`.
5. `run_lua` with `return "hello"` -> output "hello".
6. `get_job_info` and `import_vector_file` (a small DXF) -> these are **unverified**; report exactly what happens.

## 5. Report back
Call the `feedback_report` tool (works even if the bridge is not connected) and give the user its full
output, plus: exact error messages, which verify steps passed/failed, and what the Aspire gadget dialog showed
(e.g. "cannot connect", or a Lua error about `socket`/`require`). Ask the user to paste it to the developer.
Key unknown to resolve: **can an Aspire gadget `require("socket")`?** If not, say so explicitly.
