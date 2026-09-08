local fmt = require("./format.luau")
local text = fmt.text
local opened = false
local busy = false
local errorCode = nil
local lastAttempt = 0
local codexPath = noctalia.getConfig("codex_path") or ""
local snapshot = noctalia.state.get("snapshot")
if noctalia.state.get("snapshot_path") ~= codexPath then snapshot = nil end

local function quotaCard(bucket)
  local children = {
    ui.row({ align = "center", justify = "space_between", gap = 8 }, {
      ui.label({ text = bucket.id == "codex" and "Codex" or bucket.name, fontSize = 16, fontWeight = "bold", flexGrow = 1 }),
      ui.label({ text = string.upper(bucket.plan or ""), fontSize = 11, color = "on_surface_variant" }),
    }),
  }
  for _, window in ipairs(bucket.windows) do
    local used = window.usedPercent
    local color = used >= 90 and "error" or "primary"
    table.insert(children, ui.column({ gap = 7 }, {
      ui.row({ align = "center", justify = "space_between", gap = 6 }, {
        ui.label({ text = fmt.window(window.windowDurationMins), fontSize = 13, flexGrow = 1 }),
        ui.label({ text = string.format(text("%.0f%% left · %.0f%% used", "남음 %.0f%% · 사용 %.0f%%"), 100 - used, used), fontSize = 12, color = color }),
      }),
      ui.progress({ progress = (100 - used) / 100, height = 7, radius = 4, fill = color, track = "on_surface/0.12" }),
      ui.label({ text = fmt.reset(window.resetsAt), fontSize = 12, color = "on_surface_variant" }),
      ui.label({ text = fmt.countdown(window.resetsAt), fontSize = 12, color = "on_surface_variant" }),
    }))
  end
  return ui.column({ gap = 14, padding = 16, fill = "surface_variant/0.55", radius = 12 }, children)
end

local function render()
  if not opened then return end
  local rows = {}
  if errorCode then
    table.insert(rows, ui.label({ text = fmt.error(errorCode), fontSize = 13, maxLines = 4, color = "error" }))
  end
  if snapshot and #snapshot.buckets > 0 then
    if errorCode then
      table.insert(rows, ui.label({ text = text("Last successful reading · may be out of date", "마지막 조회 결과 · 최신 정보가 아닐 수 있습니다"), fontSize = 12, color = "on_surface_variant" }))
    end
    for _, bucket in ipairs(snapshot.buckets) do
      table.insert(rows, quotaCard(bucket))
    end
  elseif not errorCode then
    table.insert(rows, ui.label({ text = text("Reading Codex usage…", "Codex 사용량을 불러오는 중…"), fontSize = 14, color = "on_surface_variant" }))
  end
  local footer = busy and text("Refreshing…", "새로고침 중…") or ""
  if not busy and snapshot then
    footer = text("Updated ", "조회 ") .. noctalia.formatTime("%m-%d %H:%M:%S", snapshot.fetchedAt)
  end
  panel.render(ui.column({ flexGrow = 1, gap = 14 }, {
    ui.row({ align = "center", gap = 8 }, {
      ui.glyph({ name = "chart-bar", size = 22, color = "primary" }),
      ui.label({ text = text("Codex Usage", "Codex 사용량"), fontSize = 18, fontWeight = "bold", flexGrow = 1 }),
      ui.button({ glyph = "refresh", tooltip = text("Refresh (R)", "새로고침 (R)"), enabled = not busy, onClick = "onRefresh", controlSize = "sm" }),
      ui.button({ glyph = "close", tooltip = text("Close", "닫기"), onClick = "onCloseClicked", controlSize = "sm" }),
    }),
    ui.scroll({ flexGrow = 1, gap = 12 }, rows),
    ui.label({ text = footer, fontSize = 11, color = "on_surface_variant" }),
  }))
end

local function refresh()
  if not opened or busy or os.time() - lastAttempt < 15 then return end
  lastAttempt = os.time()
  if noctalia.getSetting("shell.offline_mode") == true then
    errorCode = "offline"
    render()
    return
  end
  if not noctalia.commandExists("python3") then
    errorCode = "python_missing"
    render()
    return
  end
  busy = true
  errorCode = nil
  render()
  local accepted = noctalia.runAsync({ "python3", noctalia.pluginDir() .. "/bridge.py", "--codex", codexPath }, function(result)
    busy = false
    local data = nil
    if result.exitCode == 0 and not result.stdoutTruncated then
      data = noctalia.json.decode(result.stdout)
    end
    if type(data) == "table" and data.ok == true and type(data.buckets) == "table" then
      snapshot = data
      errorCode = nil
      noctalia.state.set("snapshot_path", codexPath)
      noctalia.state.set("snapshot", snapshot)
    else
      errorCode = result.timedOut and "timeout" or (type(data) == "table" and data.error or "request_failed")
      if errorCode == "login_required" or errorCode == "chatgpt_required" or errorCode == "no_limits" then
        snapshot = nil
        noctalia.state.set("snapshot", nil)
      end
    end
    render()
  end, 30000)
  if not accepted then
    busy = false
    errorCode = "request_failed"
    render()
  end
end

function onOpen(_context)
  opened = true
  render()
  refresh()
end

function onClose()
  opened = false
end

function update()
  if not opened then return end
  local interval = math.max(60, noctalia.getConfig("refresh_seconds") or 300)
  if os.time() - lastAttempt >= interval then refresh() end
  render()
end

function onRefresh() refresh() end
function onCloseClicked() panel.close() end
function onKey(chord, pressed)
  if chord == "r" and pressed then refresh() end
end

noctalia.setUpdateInterval(60000)
