# Noctalia Codex Usage

단축키로 열고 닫는 Noctalia 5용 Codex 사용량 패널입니다. Noctalia 본체를 수정하거나 다시 빌드하지 않습니다.

- **Cmd/Super + Shift + U**: 사용량 패널 열기 / 닫기 (Umbriel 기본 설치)
- **R** 또는 새로고침 버튼: 사용량 조회
- **Esc**, 닫기 버튼, 패널 바깥 클릭으로도 닫을 수 있습니다.
- 게이지는 **남은 한도**입니다. 26%를 사용했다면 74% 채워집니다.
- 계정에서 반환한 한도별 사용률, 남은 비율, 초기화 날짜·시각 및 남은 시간을 표시합니다.
- 서버가 제공하는 모든 한도를 기본으로 표시합니다. 내용이 길면 패널 안에서 스크롤할 수 있습니다.
- 시스템 언어를 따라 한국어/영어로 표시합니다. 플러그인 설정에서 바꿀 수 있습니다.

이 패널은 Control Center의 탭이 아닙니다. 독립적인 Noctalia 패널이며,
현재 열려 있는 일반 패널을 대체하여 표시됩니다. 기존 Cmd+D는 그대로 사용합니다.

## 설치

필요한 환경:

- Linux Wayland, Noctalia 5 (plugin API 26 이상; **5.0.1에서 확인**)
- Python 3.11 이상 (추가 pip 패키지 없음)
- ChatGPT 계정으로 로그인한 Codex CLI (**0.153.4에서 확인**)
- Git (저장소를 복제하고 업데이트할 때)

Codex가 없다면 [공식 설치 안내](https://developers.openai.com/codex/cli/)에 따라 설치한 다음
터미널에서 `codex login`으로 로그인합니다. 기기마다 로그인하며 인증 파일을 저장소에 넣지 않습니다.

이 저장소를 복제한 디렉터리에서:

```sh
python3 install.py --check
python3 install.py
```

설치 프로그램은 현재 체크아웃을 Noctalia의 `codex-usage` 소스로 등록하고 플러그인을 활성화합니다.
Umbriel 세션에서는 `Mod+Shift+U` 단축키도 설정합니다. 기존 키와 충돌하면 덮어쓰지 않고 중단합니다.
설정 변경 전 백업 경로를 출력하며, 다시 실행해도 같은 키가 중복 등록되지 않습니다.
**설치 후에도 이 저장소 디렉터리를 보관하세요.** Noctalia가 이곳의 파일을 직접 읽습니다.

다른 단축키 또는 명시적인 Umbriel 설정 파일:

```sh
python3 install.py --shortcut Mod+Alt+U
python3 install.py --umbriel-config ~/.config/umbriel/config.toml
```

GPD WIN mini나 OS/셸 재설치 후에도 같은 순서로 의존성 설치 → Codex 로그인 → 저장소 복제 →
`python3 install.py`를 실행하면 됩니다. 모니터 이름, 해상도, 개인 홈 경로를 플러그인에 고정하지 않습니다.
GPD WIN mini 실기기 검증은 아직 하지 않았습니다. 패널은 460×400 논리 픽셀이며, 추가 한도는 내부 스크롤로 확인합니다.

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
Codex CLI가 로그인과 인증 갱신을 처리합니다.

패널을 열 때 조회하며 연속 요청은 15초 간격으로 제한합니다. 열어 둔 동안의 기본 갱신 간격은 5분입니다.
패널이 닫히면 주기적 조회를 중단합니다. 이미 시작한 조회의 타임아웃은 20초이며 이후 자식 프로세스를 정리합니다.
상주 백그라운드 수집 서비스는 없습니다. 최근 성공 결과는 Noctalia 실행 중 메모리에만 보관합니다.
Noctalia 오프라인 모드를 존중합니다.

주간 한도가 `primary`에 올 수도 있으므로, 기간은 `windowDurationMins`에서 읽습니다.
서버가 5시간 한도를 보내지 않으면 만들어서 표시하지 않습니다. 초기화 시각은 `resetsAt`의 Unix 초를
시스템 현지 시간으로 표시합니다. 과거 초기화 시각만으로 한도가 새로 충전되었다고 추정하지 않습니다.
조회 실패 시 이전 결과에는 최신 정보가 아닐 수 있다는 표시가 붙습니다.
ChatGPT 구독 한도용이며 API 키 요금이나 토큰별 청구액 조회는 지원하지 않습니다.

Noctalia 설정 → Plugins → Codex Usage에서 실행 파일 경로, 언어, 갱신 주기를 바꿀 수 있습니다.
CLI가 PATH에 없다면 `~/.local/bin`, Linuxbrew, `/usr/local/bin`, `/usr/bin`도 확인합니다.
CLI 경로에는 실행 파일만 입력하며 셸 명령이나 인자를 넣지 않습니다.

문제 확인:

```sh
python3 codex_usage/bridge.py
noctalia plugins lint codex_usage
```

## 업데이트와 제거

```sh
git pull --ff-only
python3 install.py
```

플러그인 스크립트는 자동으로 다시 로드됩니다. 매니페스트 변경도 설치 프로그램의 활성화 단계에서 반영합니다.

```sh
python3 install.py --uninstall
```

플러그인을 비활성화하고 이 소스 등록 및 일치하는 기본 단축키를 제거합니다.
직접 키를 바꿨다면 설치할 때와 같은 `--shortcut`을 전달하세요.
소스 코드, 백업, Noctalia의 플러그인 환경설정은 보존됩니다.

## 개발 및 검증

```sh
python3 -m unittest discover -s tests -v
lua tests/test_panel.lua
noctalia plugins lint codex_usage
```

테스트는 실제 계정에 접속하지 않습니다. 실사용 확인은 패널을 열어 실제 조회 결과를 확인하고,
같은 단축키로 닫히는지 점검합니다.

구조: `codex_usage/plugin.toml`은 플러그인 등록 정보, `panel.luau`는 표시와 갱신,
`bridge.py`는 공식 CLI 통신, `format.luau`는 날짜와 언어 처리입니다.
`catalog.toml`을 포함하므로 나중에 GitHub 저장소를 Noctalia의 Git 소스로 직접 등록할 수도 있습니다.
