# Prompt Generator for Images and Videos

이미지 생성 AI를 위한 프롬프트 생성 도구. 랜덤 조합 기반의 프롬프트를 생성하고, 외부 LLM을 통해 개선 및 번역함.

## 주요 기능

- 카테고리 기반 랜덤 프롬프트 생성 (카테고리별 `랜덤` / `제외` / `LLM` / 직접 선택)
- 외부 LLM을 통한 프롬프트 개선 및 한국어 번역 (OpenAI / Gemini / Claude / OpenAI 호환 API)
- 앱 실행 시 외부 LLM 자동 연결. 연결되지 않으면 프롬프트 생성 불가
- `models.json` 을 통한 외부 LLM 모델 확장 설정 및 최근 사용 모델 자동 기억
- 프롬프트 방식 선택 (레거시 태그형 / 최신 모델용 자연어형)
- 자연스러운 사진 모드 (AI 티 제거 지시문)
- 비디오 생성용 모드 (유튜브 쇼츠·틱톡 대상 8~10초 세로 숏폼 프롬프트)
- Dynamic Prompts 와일드카드 치환 (`__hair__` → `hair.txt` 의 임의 한 줄)
- 프롬프트 히스토리 저장 및 관리
- 클립보드 복사 기능

## 요구 사항

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (Python 패키지 관리자)
- 외부 LLM API 키 (필수)

## API 키 설정

외부 LLM 사용 시 환경변수에 API 키 설정이 필요함.  아래와 같이 `.env` 파일을 사용하여 간편하게 관리할 수 있음.

1. `.env.example` 파일을 복사하여 `.env` 파일 생성
2. `.env` 파일에 소유한 API 키 입력

```bash
# .env 파일 예시
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...
ANTHROPIC_API_KEY=sk-ant...
OPENROUTER_API_KEY=sk-or-...

# Dynamic Prompts 와일드카드 디렉토리 기본값 (선택)
DYNAMYC_PROMPTS_DEFAULT_ROOT=H:\ComfyUI\custom_nodes\comfyui-dynamicprompts\wildcards
```

또는 직접 환경변수로 설정할 수도 있음:

```bash
# Windows
set OPENAI_API_KEY=your-openai-key
set GEMINI_API_KEY=your-gemini-key
set ANTHROPIC_API_KEY=your-anthropic-key

# Linux/Mac
export OPENAI_API_KEY=your-openai-key
export GEMINI_API_KEY=your-gemini-key
export ANTHROPIC_API_KEY=your-anthropic-key
```

사용할 환경변수 이름은 `models.json` 의 `api_key` 항목으로 결정되므로, 모델을 추가할 때 원하는 이름을 자유롭게 지정할 수 있음.

## 외부 LLM 모델 설정 (`models.json`)

사용할 외부 LLM 모델은 프로젝트 루트의 `models.json` 에서 관리함. 목록을 수정하면 사이드바 모델 선택 콤보박스에 그대로 반영됨.

```json
[
  {
    "provider": "openai",
    "model": "gpt-5.6-luna",
    "api_key": "OPENAI_API_KEY"
  },
  {
    "provider": "gemini",
    "model": "gemini-3.5-flash-lite",
    "api_key": "GEMINI_API_KEY"
  },
  {
    "provider": "anthropic",
    "model": "claude-haiku-4-5",
    "api_key": "ANTHROPIC_API_KEY"
  },
  {
    "provider": "openai_compat",
    "model": "deepseek/deepseek-v4-flash-latest",
    "api_key": "OPENROUTER_API_KEY",
    "base_url": "https://openrouter.ai/api/v1"
  }
]
```

필드 설명:

| 필드 | 필수 | 설명 |
| --- | --- | --- |
| `provider` | O | `openai`, `gemini`, `anthropic`, `openai_compat` 중 하나 |
| `model` | O | API에 전달할 모델명. 콤보박스 표시명으로도 사용됨 |
| `api_key` | O | API 키 값이 아니라 **키가 담긴 환경변수 이름**. 실제 값은 환경변수 또는 `.env` 에서 읽음 |
| `base_url` | △ | `openai_compat` 에서만 필수. OpenAI 호환 엔드포인트의 루트 URL |

참고 사항:

- `api_key` 에 API 키를 직접 적지 말 것. 반드시 환경변수 이름만 기재함.
- 앱 실행 시 목록의 **첫 번째 모델**이 기본 선택되며, 이후에는 마지막으로 선택한 모델이 `user_settings.json` 에 저장되어 자동 선택됨.
- 앱을 실행하면 선택된 모델로 **자동 연결**을 시도함. 연결 실패 시 사이드바에 원인이 표시되고 프롬프트 생성 버튼이 비활성화됨.
- `base_url` 에 `/chat/completions` 까지 적어도 내부에서 루트 URL 로 정규화함.
- `models.json` 에 오류가 있으면 사이드바에 원인 메시지가 표시됨.

## 설치 및 실행

### 방법 1. 전역 명령어로 설치 (권장)

`promptgen` 명령을 어느 디렉토리에서나 실행할 수 있도록 설치함.

```bash
# 프로젝트 루트에서 실행
uv tool install --editable .

# 실행 파일 경로를 PATH에 등록 (최초 1회)
uv tool update-shell
```

설치 후 터미널을 재시작하면 아무 위치에서나 아래 명령으로 실행 가능함.

```bash
promptgen
```

Streamlit 옵션을 그대로 전달할 수 있음.

```bash
promptgen --server.port 8080 --server.headless true
```

참고 사항:

- `--editable` 설치이므로 소스를 수정하면 즉시 반영됨. 단, 프로젝트 디렉토리를 이동하거나 삭제하면 실행되지 않음.
- 의존성이 변경된 경우 `uv tool install --editable . --force`로 재설치함.
- `.env`, `models.json`, `prompt_history.json`, `user_settings.json` 은 실행 위치와 무관하게 항상 프로젝트 루트를 기준으로 처리됨.
- 제거하려면 `uv tool uninstall prompt-generator-for-images-and-videos`를 실행함.

### 방법 2. 프로젝트 디렉토리에서 직접 실행

```bash
# 의존성 설치
uv sync

# 실행
uv run streamlit run app.py
```

## 프로젝트 구조

```
├── app.py                 # Streamlit 메인 앱
├── promptgen_cli.py       # promptgen 콘솔 스크립트 진입점
├── models.json            # 외부 LLM 모델 목록 설정
├── core/
│   └── prompt_engine.py   # 프롬프트 생성 엔진
├── data/
│   ├── prompt_database.py # 프롬프트 데이터베이스
│   └── llm_prompts.py     # LLM 개선/번역/비디오 모드 시스템 프롬프트
├── integrations/
│   ├── model_config.py    # models.json 로더
│   └── external_llm_integration.py # 외부 LLM 연동 (OpenAI/Gemini/Claude/OpenAI 호환)
├── utils/
│   ├── history_manager.py  # 히스토리 관리
│   ├── settings_manager.py # 최근 선택 모델 등 사용자 설정
│   ├── wildcard_manager.py # Dynamic Prompts 와일드카드 치환
│   └── logger.py           # LLM 호출 로깅
└── requirements.txt       # 의존성 목록
```

## 사용 방법

1. 앱 실행 시 사이드바 최상단의 외부 LLM이 자동 연결됨. 필요하면 모델을 바꾸고 "연결" 버튼을 누름
2. 프롬프트 모드(SFW/NSFW), 아트 스타일, 프롬프트 방식을 선택함
3. 필요 시 옵션을 조정함
   - 자연스러운 사진 모드: 실사 스타일에서 AI 티를 줄이는 지시문을 부착함
   - 비디오 생성용: 8~10초 9:16 숏폼 영상 프롬프트로 재작성함 (이때 자연스러운 사진 모드는 적용되지 않음)
   - Dynamic Prompts Directory: 와일드카드 `.txt` 파일이 있는 디렉토리를 지정함
4. 세부 카테고리를 설정함
   - `랜덤`: 해당 카테고리에서 임의 선택
   - `제외`: 프롬프트에서 제외
   - `LLM`: 항목을 비워두고 LLM이 상상해서 채우도록 위임
5. 사용자 요구사항에 `__hair__` 처럼 적으면 지정한 디렉토리의 `hair.txt` 에서 임의의 한 줄로 치환됨 (서브디렉토리는 탐색하지 않음)
6. "프롬프트 생성" 버튼을 클릭함
7. 생성된 영문 프롬프트와 한글 번역의 복사 버튼을 눌러 이미지/영상 생성 AI에 사용함

## 사용자 설정 저장

`user_settings.json` 에 모드, 스타일, 프롬프트 방식, 체크박스 옵션, 비디오 모드, 카테고리 선택, 마지막 사용 모델, 와일드카드 디렉토리 등이 저장되어 다음 실행 시 복원됨.
