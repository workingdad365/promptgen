# Prompt Generator for Images

이미지 생성 AI를 위한 프롬프트 생성 도구. 랜덤 조합 기반의 프롬프트를 생성하고, LLM을 통해 개선 및 번역 기능을 제공함.

## 주요 기능

- 카테고리 기반 랜덤 프롬프트 생성
- LLM을 통한 프롬프트 개선 (Ollama / OpenAI / Gemini / Claude / OpenAI 호환 API)
- `models.json` 을 통한 외부 LLM 모델 확장 설정
- 최근 사용한 모델 자동 기억
- LLM 또는 Google Translate를 통한 한국어 번역
- 프롬프트 히스토리 저장 및 관리
- 클립보드 복사 기능

## 요구 사항

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (Python 패키지 관리자)

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

Ollama 사용 시에는 별도 API 키 없이 로컬 서버 연결만 필요.

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
- 제거하려면 `uv tool uninstall prompt-generator-for-images`를 실행함.

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
│   └── prompt_database.py # 프롬프트 데이터베이스
├── integrations/
│   ├── model_config.py    # models.json 로더
│   ├── ollama_integration.py      # Ollama 연동
│   └── external_llm_integration.py # 외부 LLM 연동 (OpenAI/Gemini/Claude/OpenAI 호환)
├── utils/
│   ├── history_manager.py # 히스토리 관리
│   ├── settings_manager.py # 최근 선택 모델 등 사용자 설정
│   └── translation.py     # 번역 유틸리티
└── requirements.txt       # 의존성 목록
```

## 사용 방법

1. 좌측 사이드바에서 모드 선택 (SFW/NSFW)
2. LLM 연결 (외부 LLM 또는 Ollama)
3. "프롬프트 생성" 버튼 클릭
4. 생성된 영문 프롬프트 우측 복사 버튼 클릭하여 이미지 생성 AI에 사용
