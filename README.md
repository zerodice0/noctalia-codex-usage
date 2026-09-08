# Noctalia Codex Usage

A keyboard-toggleable Noctalia 5 panel for Codex remaining quota and reset times. Korean and English UI; no shell patches or extra Python packages required.

단축키로 열고 닫는 Noctalia 5용 Codex 사용량 패널입니다. Noctalia 본체를 수정하거나 다시 빌드하지 않습니다.
OpenAI나 Noctalia의 공식 플러그인이 아닌 독립 프로젝트입니다.

- **Cmd/Super + Shift + U**: 사용량 패널 열기 / 닫기 (Umbriel 기본 설치)
- **R** 또는 새로고침 버튼: 사용량 조회
- **Esc**, 닫기 버튼, 패널 바깥 클릭으로도 닫을 수 있습니다.
- 게이지는 **남은 한도**입니다. 26%를 사용했다면 74% 채워집니다.
- 계정에서 반환한 한도별 사용률, 남은 비율, 초기화 날짜·시각 및 남은 시간을 표시합니다.
- Pro 등의 요금제 이름은 패널 제목에 한 번만 표시합니다.
- 서버가 제공하는 모든 한도를 기본으로 표시합니다. 화면에 여유가 있으면 스크롤 없이 확인하며, 작은 화면이나 한도가 더 많은 계정에서는 패널 안에서 스크롤할 수 있습니다.
- 시스템 언어를 따라 한국어/영어로 표시합니다. 플러그인 설정에서 바꿀 수 있습니다.

이 패널은 Control Center의 탭이 아닙니다. 독립적인 Noctalia 패널이며,
현재 열려 있는 일반 패널을 대체하여 표시됩니다. 기존 Cmd+D는 그대로 사용합니다.

## 설치

필요한 환경:

- Linux Wayland, Noctalia 5 (plugin API 26 이상; **5.0.1에서 확인**)
- Python 3.11 이상 (추가 pip 패키지 없음)
- ChatGPT 계정으로 로그인한 Codex CLI (**0.153.4에서 확인**)
- Git (저장소를 복제하고 업데이트할 때)

Noctalia가 실행 중인 데스크톱 세션의 터미널에서 **일반 사용자로** 설치하세요. `sudo`는 사용하지 않습니다.
설치 프로그램은 Noctalia·Python·Codex 자체를 설치하거나 Codex 로그인을 대신하지 않습니다.
Noctalia 4용 플러그인은 아닙니다. Umbriel 환경에서 설치와 단축키 동작을 확인했으며,
다른 컴포지터에서는 아래 수동 단축키 설정을 사용합니다.

Codex가 없다면 [공식 설치 안내](https://developers.openai.com/codex/cli/)에 따라 설치한 다음
터미널에서 `codex login`으로 로그인합니다. 기기마다 로그인하며 인증 파일을 저장소에 넣지 않습니다.

계속 보관할 위치에서 저장소를 복제한 뒤 설치합니다:

```sh
git clone https://github.com/zerodice0/noctalia-codex-usage.git
cd noctalia-codex-usage
python3 install.py --check
python3 install.py
```

`--check`는 변경 없이 실행 중인 Noctalia와 플러그인 lint, 소스 등록 경로, 적용할 단축키의 충돌을 확인합니다.
Codex 로그인과 실제 한도 조회까지 검증하지는 않습니다. 설치 후 **Cmd/Super + Shift + U**로 패널을 열어 조회 결과를 확인하세요.

설치 프로그램은 현재 체크아웃을 Noctalia의 `codex-usage` 소스로 등록하고 플러그인을 활성화합니다.
Umbriel 세션에서는 `Mod+Shift+U` 단축키도 설정합니다. 기존 키와 충돌하면 덮어쓰지 않고 중단합니다.
설정을 수정할 때 원본을 백업하고 `umbriel validate`를 통과한 설정만 적용하며, 완료 후 백업 경로를 출력합니다.
다시 실행해도 같은 키가 중복 등록되지 않습니다.
**설치 후에도 이 저장소 디렉터리를 보관하세요.** Noctalia가 이곳의 파일을 직접 읽습니다.

처음부터 다른 단축키를 쓰거나 Umbriel 설정 파일을 직접 지정할 수 있습니다:

```sh
python3 install.py --shortcut Mod+Alt+U
python3 install.py --umbriel-config ~/.config/umbriel/config.toml
```

`--shortcut`은 지정한 키를 등록할 뿐, 전에 등록한 다른 키를 자동으로 지우지는 않습니다.
이미 설치한 뒤 키를 바꾼다면 Umbriel 설정에서 이전 키를 제거하세요.
사용자 지정 키·설정 경로를 선택했다면 이후 점검·업데이트·제거 때에도 같은 옵션을 전달하세요.

### 새 기기 및 재설치

GPD WIN mini나 OS/셸 재설치 후에도 같은 순서로 의존성 설치 → Codex 로그인 → 저장소 복제 →
`python3 install.py`를 실행하면 됩니다. 모니터 이름, 해상도, 개인 홈 경로를 플러그인에 고정하지 않습니다.
GPD WIN mini 실기기 검증은 아직 하지 않았습니다. 기본 패널은 520×700 논리 픽셀이며,
확인한 3개 한도 그룹·4개 기간 항목은 데스크톱에서 스크롤 없이 표시됩니다.
화면의 사용 가능한 영역보다 크면 Noctalia가 크기를 제한하며, 이때 넘치는 내용은 내부 스크롤로 확인합니다.

## 다른 Wayland 컴포지터

```sh
python3 install.py --no-shortcut
```

아래 명령을 원하는 단축키에 연결하면 됩니다. 같은 명령이 열기/닫기를 모두 처리합니다.

```sh
noctalia msg panel-toggle zerodice0/codex_usage:panel
```

예: Niri의 `binds` 안에:

```kdl
Mod+Shift+U { spawn "noctalia" "msg" "panel-toggle" "zerodice0/codex_usage:panel"; }
```

예: Hyprland의 전통적인 설정 문법:

```ini
bind = SUPER SHIFT, U, exec, noctalia msg panel-toggle zerodice0/codex_usage:panel
```

다른 컴포지터의 단축키 설정은 자동으로 편집하지 않습니다. 위 예시는 Umbriel 외 환경에서는 별도 검증이 필요합니다.

## 데이터와 갱신

[공식 Codex App Server](https://developers.openai.com/codex/app-server)의 stdio JSON-RPC를 사용합니다.
호출은 `initialize` → `initialized` → `account/rateLimits/read`뿐입니다.
모델 작업이나 대화를 시작하지 않으며, 플러그인이 인증 파일이나 대화 기록을 직접 읽지 않습니다.
Codex CLI가 로그인과 인증 갱신을 처리하므로 조회에는 네트워크 연결이 필요합니다.
플러그인은 한도 표시용 필드만 받아 사용하며, 원본 서버 오류 메시지나 인증정보를 패널에 전달하지 않습니다.
플러그인 자체는 별도의 서버로 데이터를 전송하지 않습니다. Codex CLI 자체의 데이터 저장·통신은 별개입니다.

패널을 열 때 조회하며 연속 요청은 15초 간격으로 제한합니다. 열어 둔 동안의 기본 갱신 간격은 5분입니다.
패널이 닫히면 주기적 조회를 중단합니다. 이미 시작한 조회의 타임아웃은 20초이며 이후 자식 프로세스를 정리합니다.
상주 백그라운드 수집 서비스는 없습니다. 최근 성공 결과는 Noctalia 실행 중 메모리에만 보관합니다.
Noctalia 오프라인 모드를 존중합니다.

주간 한도가 `primary`에 올 수도 있으므로, 기간은 `windowDurationMins`에서 읽습니다.
서버가 5시간 한도를 보내지 않으면 만들어서 표시하지 않습니다. 초기화 시각은 `resetsAt`의 Unix 초를
시스템 현지 시간으로 표시합니다. 과거 초기화 시각만으로 한도가 새로 충전되었다고 추정하지 않습니다.
일반적인 조회 실패 시 이전 결과에는 최신 정보가 아닐 수 있다는 표시가 붙습니다.
로그인이 필요하거나 계정 한도가 없다는 응답을 받으면 이전 결과를 지웁니다.
ChatGPT 구독 한도용이며 API 키 요금이나 토큰별 청구액 조회는 지원하지 않습니다.

Noctalia 설정 → Plugins → Codex Usage에서 실행 파일 경로, 언어, 갱신 주기를 바꿀 수 있습니다.
CLI가 PATH에 없다면 `~/.local/bin`, Linuxbrew, `/usr/local/bin`, `/usr/bin`도 확인합니다.
CLI 경로에는 실행 파일만 입력하며 셸 명령이나 인자를 넣지 않습니다.

### 문제 해결

우선 저장소 디렉터리에서 확인합니다. 첫 명령은 실제 계정의 한도 정보를 조회합니다.

```sh
python3 codex_usage/bridge.py
noctalia plugins lint codex_usage
```

진단 결과를 공유할 때는 사용량·초기화 시각 등 공개하고 싶지 않은 계정 정보를 지우세요.
인증 파일이나 토큰은 첨부하지 마세요.

| 증상 | 확인할 내용 |
| --- | --- |
| 설치 시 Noctalia 연결 실패 | Noctalia가 실행 중인 같은 사용자·데스크톱 세션에서 설치했는지 확인합니다. |
| CLI를 찾지 못함 (`codex_missing`) | 플러그인 설정에서 Codex 실행 파일의 절대 경로를 지정합니다. 터미널과 GUI의 PATH가 다를 수 있습니다. |
| 로그인 필요 / API 키 계정 | 같은 사용자로 `codex login`을 실행해 ChatGPT 계정으로 로그인합니다. |
| 시간 초과 / 오프라인 / 조회 실패 | 네트워크와 Noctalia 오프라인 모드를 확인하고 15초 이상 지난 뒤 새로고침합니다. |
| 5시간 한도가 안 보임 | 서버가 해당 기간을 반환하지 않으면 표시하지 않습니다. 모든 계정이 같은 항목을 반환하지는 않습니다. |
| 단축키가 충돌함 | 다른 `--shortcut`을 선택하거나 `--no-shortcut`으로 설치한 뒤 직접 연결합니다. |
| `Source 'codex-usage' points elsewhere` | 기존 등록 경로와 다른 곳에서 실행한 경우입니다. 원래 체크아웃을 사용하거나 Noctalia의 소스 설정을 정리한 뒤 새 경로에서 설치합니다. |
| 한국어 대신 영어로 표시됨 | 플러그인 언어를 한국어로 지정합니다. 자동 모드는 Noctalia 프로세스의 `LC_ALL`, `LC_MESSAGES`, `LANG` 순서로 확인합니다. |

## 업데이트와 제거

설치할 때 사용한 저장소 디렉터리에서 실행합니다:

```sh
git pull --ff-only
python3 install.py
```

로컬 경로 소스를 사용하는 설치 방식이므로 업데이트는 이 체크아웃에서 `git pull`로 받습니다.
`--no-shortcut`, `--shortcut`, `--umbriel-config`를 사용했다면 `install.py`에 같은 옵션을 덧붙이세요.
플러그인 스크립트는 자동으로 다시 로드됩니다. Noctalia 5.0.1에서는 매니페스트의 패널 크기를 바꿔도
기존 패널 인스턴스가 이전 크기를 유지할 수 있습니다. 크기 변경이 포함된 업데이트는 Noctalia를 다시 시작하면 반영됩니다.

제거할 때도 Noctalia가 실행 중이어야 합니다:

```sh
python3 install.py --uninstall
```

플러그인을 비활성화하고 이 소스 등록 및 지정된 키에 연결된 일치하는 단축키를 제거합니다.
기본값은 `Mod+Shift+U`입니다. 사용자 지정 설치 옵션을 사용했다면 제거 때에도 같은 옵션을 전달하세요.
다른 컴포지터에서 직접 추가한 단축키는 해당 설정에서 직접 제거합니다.
소스 코드, 백업, Noctalia의 플러그인 환경설정은 보존됩니다.

## 개발 및 검증

아래 검증에는 Python 외에 `lua`와 `noctalia` 명령이 필요합니다. Lua CLI는 테스트용이며 설치·사용에는 필요하지 않습니다.

```sh
python3 -m unittest discover -s tests -v
lua tests/test_panel.lua
noctalia plugins lint codex_usage
```

테스트는 실제 계정에 접속하지 않습니다. 실사용 확인은 패널을 열어 실제 조회 결과를 확인하고,
같은 단축키로 닫히는지 점검합니다.

구조: `codex_usage/plugin.toml`은 플러그인 등록 정보, `panel.luau`는 표시와 갱신,
`bridge.py`는 공식 CLI 통신, `format.luau`는 날짜와 언어 처리입니다.
`catalog.toml`은 Noctalia가 읽는 플러그인 목록입니다. 위 설치 프로그램은 이 저장소를 로컬 경로 소스로 등록합니다.

## 라이선스 및 문의

[MIT 라이선스](LICENSE)로 배포합니다. 버그 제보와 개선 제안은
[GitHub Issues](https://github.com/zerodice0/noctalia-codex-usage/issues)에 남겨 주세요.
Noctalia·Codex CLI 버전, 컴포지터, 재현 절차를 포함하면 확인에 도움이 됩니다.
