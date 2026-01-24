# Prompt Generator for Images

이미지 생성 AI를 위한 프롬프트 생성 도구. 랜덤 조합 기반의 프롬프트를 생성하고, LLM을 통해 개선 및 번역 기능을 제공함.

## 주요 기능

- 카테고리 기반 랜덤 프롬프트 생성
- LLM을 통한 프롬프트 개선 (Ollama / OpenAI / Gemini / Claude)
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

Ollama 사용 시에는 별도 API 키 없이 로컬 서버 연결만 필요.

## 설치 및 실행

```bash
# 의존성 설치
uv sync

# 실행
uv run streamlit run app.py
```

## 프로젝트 구조

```
├── app.py                 # Streamlit 메인 앱
├── core/
│   └── prompt_engine.py   # 프롬프트 생성 엔진
├── data/
│   └── prompt_database.py # 프롬프트 데이터베이스
├── integrations/
│   ├── ollama_integration.py      # Ollama 연동
│   └── external_llm_integration.py # 외부 LLM 연동 (OpenAI/Gemini/Claude)
├── utils/
│   ├── history_manager.py # 히스토리 관리
│   └── translation.py     # 번역 유틸리티
└── requirements.txt       # 의존성 목록
```

## 사용 방법

1. 좌측 사이드바에서 모드 선택 (SFW/NSFW)
2. LLM 연결 (외부 LLM 또는 Ollama)
3. "프롬프트 생성" 버튼 클릭
4. 생성된 영문 프롬프트 우측 복사 버튼 클릭하여 이미지 생성 AI에 사용
