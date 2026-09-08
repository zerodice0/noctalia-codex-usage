local M = {}
local language = noctalia.getConfig("language") or "auto"
if language == "auto" then
  local locale = noctalia.getenv("LC_ALL") or noctalia.getenv("LC_MESSAGES") or noctalia.getenv("LANG") or "en"
  language = string.sub(locale, 1, 2) == "ko" and "ko" or "en"
end
local ko = language == "ko"

function M.text(en, korean)
  return ko and korean or en
end

function M.window(minutes)
  if minutes == 10080 then return M.text("Weekly limit", "주간 한도") end
  if minutes == 300 then return M.text("5-hour limit", "5시간 한도") end
  if minutes == 1440 then return M.text("Daily limit", "일간 한도") end
  if not minutes then return M.text("Usage limit", "사용 한도") end
  if minutes % 1440 == 0 then
    return string.format(M.text("%g-day limit", "%g일 한도"), minutes / 1440)
  end
  if minutes % 60 == 0 then
    return string.format(M.text("%g-hour limit", "%g시간 한도"), minutes / 60)
  end
  return string.format(M.text("%g-minute limit", "%g분 한도"), minutes)
end

function M.reset(timestamp)
  if not timestamp then return M.text("Reset time unavailable", "초기화 시각 정보 없음") end
  return M.text("Resets  ", "초기화  ") .. noctalia.formatTime("%Y-%m-%d %H:%M %Z", timestamp)
end

function M.countdown(timestamp)
  if not timestamp then return "" end
  local minutes = math.ceil((timestamp - os.time()) / 60)
  if minutes <= 0 then return M.text("Reset time passed · refresh to confirm", "초기화 시각 경과 · 새로고침 필요") end
  local days = math.floor(minutes / 1440)
  local hours = math.floor((minutes % 1440) / 60)
  if days > 0 then return string.format(M.text("In %dd %dh", "%d일 %d시간 후"), days, hours) end
  return string.format(M.text("In %dh %dm", "%d시간 %d분 후"), hours, minutes % 60)
end

local errors = {
  codex_missing = {"Codex CLI was not found. Install it or set its path in plugin settings.", "Codex CLI를 찾을 수 없습니다. 설치하거나 플러그인 설정에서 경로를 지정하세요."},
  login_required = {"Sign in to Codex CLI with your ChatGPT account, then refresh.", "Codex CLI에서 ChatGPT 계정으로 로그인한 뒤 새로고침하세요."},
  chatgpt_required = {"These quotas require ChatGPT sign-in. API-key billing is separate.", "이 한도는 ChatGPT 로그인 시 조회할 수 있습니다. API 키 과금은 별도입니다."},
  no_limits = {"The server did not return quota information for this account.", "서버가 이 계정의 한도 정보를 반환하지 않았습니다."},
  timeout = {"The request timed out. Check your connection and refresh.", "조회 시간이 초과되었습니다. 네트워크를 확인한 뒤 새로고침하세요."},
  upgrade_codex = {"Update Codex CLI to a version with account/rateLimits/read support.", "사용량 조회를 지원하는 최신 Codex CLI로 업데이트하세요."},
  offline = {"Noctalia offline mode is enabled.", "Noctalia 오프라인 모드가 켜져 있습니다."},
  python_missing = {"Python 3 is required to read Codex usage.", "Codex 사용량 조회에는 Python 3가 필요합니다."},
  request_failed = {"Could not fetch usage. Check your network and Codex login.", "사용량을 조회하지 못했습니다. 네트워크와 Codex 로그인 상태를 확인하세요."},
}

function M.error(code)
  local message = errors[code] or errors.request_failed
  return M.text(message[1], message[2])
end

return M
