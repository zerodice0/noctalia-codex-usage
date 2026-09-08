-- Behavioral tests of the panel using a minimal host, without network or GUI.
local now = 100000
os.time = function() return now end
local calls, renders = 0, 0
local pending, tree
local state = {}
local decoded
local offline = false
local originalRequire = require

noctalia = {
  getConfig = function(key)
    return ({language = "ko", codex_path = "", refresh_seconds = 300})[key]
  end,
  getSetting = function() return offline end,
  commandExists = function() return true end,
  pluginDir = function() return "/plugin with spaces" end,
  setUpdateInterval = function() end,
  formatTime = function(_, timestamp) return tostring(timestamp) end,
  state = {
    get = function(key) return state[key] end,
    set = function(key, value) state[key] = value end,
  },
  json = {decode = function() return decoded end},
  runAsync = function(argv, callback, timeout)
    assert(type(argv) == "table" and argv[2] == "/plugin with spaces/bridge.py")
    assert(timeout > 22000, "Host timeout must allow the bridge to clean up its child")
    calls = calls + 1
    pending = callback
    return true
  end,
}
ui = setmetatable({}, {__index = function(_, name)
  return function(props, children) return {kind = name, props = props, children = children or {}} end
end})
panel = {
  render = function(value) renders = renders + 1; tree = value end,
  close = function() onClose() end,
}
require = function(path)
  if path == "./format.luau" then return dofile("codex_usage/format.luau") end
  return originalRequire(path)
end
dofile("codex_usage/panel.luau")

local function find(node, kind, predicate)
  if node.kind == kind and predicate(node.props) then return node end
  for _, child in ipairs(node.children) do
    local result = find(child, kind, predicate)
    if result then return result end
  end
end

local function complete(used, reset)
  decoded = {ok = true, fetchedAt = now, buckets = {
    {id = "codex", name = "Codex", plan = "pro", windows = {
      {usedPercent = used, windowDurationMins = 10080, resetsAt = reset or now + 300},
    }},
  }}
  pending({exitCode = 0, stdout = "fixture"})
end

onOpen()
assert(calls == 1)
complete(26)
assert(find(tree, "progress", function(p) return p.progress == 0.74 end), "Gauge must show remaining quota")
assert(find(tree, "label", function(p) return p.text == "남음 74% · 사용 26%" end))
assert(not find(tree, "label", function(p) return p.text == "5시간 한도" end), "Do not invent a missing 5-hour bucket")

for _, used in ipairs({0, 100}) do
  now = now + 20
  onRefresh()
  complete(used)
  assert(find(tree, "progress", function(p) return p.progress == (100 - used) / 100 end))
end

now = now + 20
onRefresh()
complete(26, now - 10)
assert(find(tree, "label", function(p) return p.text:find("초기화 시각 경과") end))
assert(find(tree, "progress", function(p) return p.progress == 0.74 end), "Past resets must not fabricate fresh quota")

now = now + 20
onRefresh()
decoded = {ok = false, error = "timeout"}
pending({exitCode = 0, stdout = "fixture"})
assert(find(tree, "label", function(p) return p.text:find("최신 정보가 아닐") end))

onClose()
local beforeCalls, beforeRenders = calls, renders
now = now + 600
update()
assert(calls == beforeCalls and renders == beforeRenders, "Closed panel must not poll or render")

offline = true
onOpen()
assert(calls == beforeCalls, "No requests in offline mode")
assert(find(tree, "label", function(p) return p.text:find("오프라인") end))
print("Panel behavior: remaining gauge, absent windows, expired resets, stale data, closed/offline polling passed")
