-- VECTRIC LUA SCRIPT
-- Aspire MCP Bridge gadget.
-- Connects to the MCP server over TCP (LuaSocket is embedded in Aspire 8.5 per
-- binary strings; availability to gadgets is UNVERIFIED) and executes Lua
-- chunks it receives. Protocol: request "<n>\n" + n bytes of Lua; reply
-- "<OK|ERR> <m>\n" + m bytes. The gadget blocks Aspire's UI while running;
-- send the chunk `return "__quit__"` (or close the socket) to release it.
-- (deliberately no `require "strict"`: it can break the embedded socket loader)

g_host = "127.0.0.1"
g_port = 8765

function main(script_path)
   local ok, socket = pcall(require, "socket")
   if not ok then
      DisplayMessageBox("MCP Bridge: require('socket') failed in this Aspire build:\n" .. tostring(socket))
      return false
   end
   local conn, err
   for attempt = 1, 10 do   -- the MCP server may still be starting
      conn, err = socket.connect(g_host, g_port)
      if conn then break end
      socket.sleep(1)
   end
   if not conn then
      DisplayMessageBox("MCP Bridge: cannot connect to " .. g_host .. ":" .. g_port .. " (" .. tostring(err) .. ")")
      return false
   end
   conn:settimeout(nil)
   while true do
      local header = conn:receive("*l")
      if not header then break end
      local n = tonumber(header)
      local code = n and conn:receive(n) or nil
      if not code then break end
      local fn, cerr = loadstring(code)
      local status, payload = "OK", ""
      if not fn then
         status, payload = "ERR", tostring(cerr)
      else
         local ok, res = pcall(fn)
         if ok then payload = tostring(res == nil and "" or res) else status, payload = "ERR", tostring(res) end
      end
      conn:send(status .. " " .. #payload .. "\n" .. payload)
      if payload == "__quit__" then break end
   end
   conn:close()
   return true
end
