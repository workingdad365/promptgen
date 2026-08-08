from typing import List, Optional, Tuple
from utils.logger import log_llm_interaction
from data.llm_prompts import (
    TRANSLATION_SYSTEM_PROMPT,
    build_enhancement_system_prompt,
)
from integrations.model_config import (
    ModelConfig,
    get_default_model,
    get_model_config,
    get_model_names,
)

# OpenAI
try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Google Gemini (새로운 google-genai SDK)
try:
    from google import genai

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Anthropic Claude
try:
    import anthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


def get_external_llm_models() -> List[str]:
    """models.json 에 등록된 모델명 목록 (첫 번째가 기본값)"""
    return get_model_names()


def get_provider_from_model(model: str) -> str:
    """모델명에서 제공자 판별"""
    config = get_model_config(model)
    return config.provider if config else "unknown"


def get_provider_label(model: str) -> str:
    """모델명에 대응하는 제공자 표시명"""
    config = get_model_config(model)
    return config.provider_label if config else "알 수 없음"


def check_api_key_for_model(model: str) -> Tuple[bool, str]:
    """모델에 맞는 API 키 확인"""
    config = get_model_config(model)
    if config is None:
        return False, f"models.json 에 등록되지 않은 모델: {model}"

    if config.api_key:
        return True, f"{config.api_key_env} 확인됨"
    return False, f"{config.api_key_env} 환경변수가 설정되지 않았습니다."


def _extract_openai_content(response) -> str:
    """OpenAI 형식 응답에서 본문 추출 (추론 전용 응답/빈 응답 방어)"""
    choice = response.choices[0]
    content = choice.message.content or getattr(choice.message, "reasoning", None)
    if content:
        return content

    finish_reason = getattr(choice, "finish_reason", None) or "unknown"
    raise RuntimeError(
        f"응답 본문이 비어 있습니다 (finish_reason={finish_reason}). "
        "출력 토큰 한도 초과 또는 콘텐츠 필터링일 수 있습니다."
    )



class ExternalLLMClient:
    """
    외부 LLM API 통합 클라이언트

    models.json 의 provider 설정에 따라 OpenAI / Gemini / Claude / OpenAI 호환 API 선택
    """

    def __init__(self, model: Optional[str] = None):
        """
        Args:
            model: 사용할 모델명 (생략 시 models.json 의 첫 번째 모델)
        """
        self.model = model or get_default_model()
        self.config: Optional[ModelConfig] = get_model_config(self.model)
        self.provider = self.config.provider if self.config else "unknown"
        self._client = None
        self._connected = False

    def test_connection(self) -> Tuple[bool, str]:
        """
        API 연결 테스트

        Returns:
            (연결 성공 여부, 메시지)
        """
        if self.config is None:
            return False, f"❌ models.json 에 등록되지 않은 모델: {self.model}"

        if self.provider == "openai":
            return self._test_openai()
        elif self.provider == "gemini":
            return self._test_gemini()
        elif self.provider == "anthropic":
            return self._test_anthropic()
        elif self.provider == "openai_compat":
            return self._test_openai_compat()

        return False, f"❌ 알 수 없는 제공자: {self.provider}"

    def _test_openai(self) -> Tuple[bool, str]:
        """OpenAI 연결 테스트"""
        if not OPENAI_AVAILABLE:
            return (
                False,
                "❌ openai 패키지가 설치되어 있지 않습니다. pip install openai 실행 필요",
            )

        api_key = self.config.api_key
        if not api_key:
            return False, f"❌ {self.config.api_key_env} 환경변수가 설정되지 않았습니다."

        try:
            self._client = OpenAI(api_key=api_key)
            # GPT-5 계열은 reasoning_effort 지원 - low로 설정하여 연결 테스트 속도 향상
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hi"}],
                max_completion_tokens=10,
                reasoning_effort="low",
            )
            self._connected = True
            return True, f"✅ OpenAI 연결 성공! (모델: {self.model})"
        except Exception as e:
            self._connected = False
            return False, f"❌ OpenAI 연결 실패: {str(e)}"

    def _test_openai_compat(self) -> Tuple[bool, str]:
        """OpenAI 호환 API 연결 테스트"""
        if not OPENAI_AVAILABLE:
            return (
                False,
                "❌ openai 패키지가 설치되어 있지 않습니다. pip install openai 실행 필요",
            )

        api_key = self.config.api_key
        if not api_key:
            return False, f"❌ {self.config.api_key_env} 환경변수가 설정되지 않았습니다."

        try:
            self._client = OpenAI(api_key=api_key, base_url=self.config.base_url)
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=10,
            )
            self._connected = True
            return True, f"✅ 연결 성공! (모델: {self.model})"
        except Exception as e:
            self._connected = False
            return False, f"❌ 연결 실패: {str(e)}"

    def _test_gemini(self) -> Tuple[bool, str]:
        """Gemini 연결 테스트"""
        if not GEMINI_AVAILABLE:
            return (
                False,
                "❌ google-genai 패키지가 설치되어 있지 않습니다. pip install google-genai 실행 필요",
            )

        api_key = self.config.api_key
        if not api_key:
            return False, f"❌ {self.config.api_key_env} 환경변수가 설정되지 않았습니다."

        try:
            self._client = genai.Client(api_key=api_key)
            response = self._client.models.generate_content(
                model=self.model, contents="Hi"
            )
            self._connected = True
            return True, f"✅ Gemini 연결 성공! (모델: {self.model})"
        except Exception as e:
            self._connected = False
            return False, f"❌ Gemini 연결 실패: {str(e)}"

    def _test_anthropic(self) -> Tuple[bool, str]:
        """Anthropic Claude 연결 테스트"""
        if not ANTHROPIC_AVAILABLE:
            return (
                False,
                "❌ anthropic 패키지가 설치되어 있지 않습니다. pip install anthropic 실행 필요",
            )

        api_key = self.config.api_key
        if not api_key:
            return False, f"❌ {self.config.api_key_env} 환경변수가 설정되지 않았습니다."

        try:
            self._client = anthropic.Anthropic(api_key=api_key)
            response = self._client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}],
            )
            self._connected = True
            return True, f"✅ Claude 연결 성공! (모델: {self.model})"
        except Exception as e:
            self._connected = False
            return False, f"❌ Claude 연결 실패: {str(e)}"

    @property
    def is_connected(self) -> bool:
        """연결 상태 반환"""
        return self._connected

    def chat(self, messages: list, max_tokens: int = 4096) -> dict:
        """
        LLM과 대화

        Args:
            messages: 대화 메시지 목록 (OpenAI 형식)
            max_tokens: 최대 토큰 수

        Returns:
            응답 딕셔너리
        """
        if not self._connected or not self._client:
            raise ConnectionError("API에 연결되어 있지 않습니다.")

        if self.provider == "openai":
            return self._chat_openai(messages, max_tokens)
        elif self.provider == "gemini":
            return self._chat_gemini(messages, max_tokens)
        elif self.provider == "anthropic":
            return self._chat_anthropic(messages, max_tokens)
        elif self.provider == "openai_compat":
            return self._chat_openai_compat(messages, max_tokens)

        raise RuntimeError(f"알 수 없는 제공자: {self.provider}")

    def _chat_openai_compat(self, messages: list, max_tokens: int) -> dict:
        """OpenAI 호환 API 채팅"""
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
            )

            content = _extract_openai_content(response)

            tokens = None
            if hasattr(response, "usage") and response.usage:
                tokens = {
                    "input": response.usage.prompt_tokens,
                    "output": response.usage.completion_tokens,
                    "total": response.usage.total_tokens,
                }

            log_llm_interaction(
                self.config.provider_label, self.model, messages, content, tokens
            )

            return {"message": {"content": content}}
        except Exception as e:
            raise RuntimeError(f"요청 실패: {str(e)}")

    def _chat_openai(self, messages: list, max_tokens: int) -> dict:
        """OpenAI 채팅"""
        try:
            # GPT-5 계열은 reasoning_effort 지원 - low로 설정하여 속도 향상
            response = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_completion_tokens=max_tokens,
                reasoning_effort="low",
            )

            content = _extract_openai_content(response)

            # 토큰 정보 추출
            tokens = None
            if hasattr(response, "usage") and response.usage:
                tokens = {
                    "input": response.usage.prompt_tokens,
                    "output": response.usage.completion_tokens,
                    "total": response.usage.total_tokens,
                }

            log_llm_interaction("OpenAI", self.model, messages, content, tokens)

            return {"message": {"content": content}}
        except Exception as e:
            raise RuntimeError(f"OpenAI 요청 실패: {str(e)}")

    def _chat_gemini(self, messages: list, max_tokens: int) -> dict:
        """Gemini 채팅"""
        try:
            # OpenAI 형식 메시지를 Gemini 형식으로 변환
            system_instruction = None
            prompt_parts = []

            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "system":
                    system_instruction = content
                elif role == "user":
                    prompt_parts.append(content)
                elif role == "assistant":
                    prompt_parts.append(f"[Previous response: {content}]")

            full_prompt = "\n\n".join(prompt_parts)

            # 시스템 프롬프트가 있으면 config에 포함
            config = {"max_output_tokens": max_tokens}
            if system_instruction:
                config["system_instruction"] = system_instruction
            response = self._client.models.generate_content(
                model=self.model, contents=full_prompt, config=config
            )

            content = response.text
            if not content:
                raise RuntimeError(
                    "응답 본문이 비어 있습니다 (안전 필터 차단 또는 토큰 한도 초과 가능)."
                )

            # 토큰 정보 추출
            tokens = None
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                tokens = {
                    "input": response.usage_metadata.prompt_token_count,
                    "output": response.usage_metadata.candidates_token_count,
                    "total": response.usage_metadata.total_token_count,
                }

            log_llm_interaction("Gemini", self.model, messages, content, tokens)

            return {"message": {"content": content}}
        except Exception as e:
            raise RuntimeError(f"Gemini 요청 실패: {str(e)}")

    def _chat_anthropic(self, messages: list, max_tokens: int) -> dict:
        """Anthropic Claude 채팅"""
        try:
            # system 메시지 분리
            system_content = ""
            user_messages = []

            for msg in messages:
                if msg.get("role") == "system":
                    system_content = msg.get("content", "")
                else:
                    user_messages.append(msg)

            response = self._client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_content if system_content else None,
                messages=user_messages,
            )

            if not response.content:
                raise RuntimeError(
                    "응답 본문이 비어 있습니다 (안전 필터 차단 또는 토큰 한도 초과 가능)."
                )
            content = response.content[0].text

            # 토큰 정보 추출
            tokens = None
            if hasattr(response, "usage") and response.usage:
                tokens = {
                    "input": response.usage.input_tokens,
                    "output": response.usage.output_tokens,
                    "total": response.usage.input_tokens + response.usage.output_tokens,
                }

            log_llm_interaction("Claude", self.model, messages, content, tokens)

            return {"message": {"content": content}}
        except Exception as e:
            raise RuntimeError(f"Claude 요청 실패: {str(e)}")


class ExternalLLMPromptEnhancer:
    """
    외부 LLM을 활용한 프롬프트 개선기
    """

    def __init__(self, client: ExternalLLMClient):
        self.client = client

    def enhance_prompt(
        self,
        original_prompt: str,
        user_requirements: Optional[str] = None,
        style: str = "photorealistic",
        natural_photo: bool = False,
    ) -> str:
        """
        프롬프트 개선

        Args:
            natural_photo: 자연스러운 사진 모드 (살 붙이기를 억제하고 AI 티 어휘를 제거)
        """
        if natural_photo and style == "photorealistic":
            user_content = f"Rewrite this prompt:\n{original_prompt}"
        else:
            user_content = f"Enhance this prompt:\n{original_prompt}"
        if user_requirements:
            user_content += f"\n\nAdditional requirements: {user_requirements}"

        system_prompt = build_enhancement_system_prompt(style, natural_photo)

        try:
            response = self.client.chat(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ]
            )
            return response["message"]["content"].strip()
        except Exception as e:
            print(f"LLM Enhancement failed: {e}")
            return original_prompt

    def translate_to_korean(self, english_prompt: str) -> str:
        """영문 프롬프트를 한글로 번역"""
        try:
            response = self.client.chat(
                messages=[
                    {"role": "system", "content": TRANSLATION_SYSTEM_PROMPT},
                    {"role": "user", "content": english_prompt},
                ]
            )
            return response["message"]["content"].strip()
        except Exception as e:
            print(f"LLM Translation failed: {e}")
            return "번역 실패"


# 하위 호환성을 위한 별칭
OpenAIClient = ExternalLLMClient
OpenAIPromptEnhancer = ExternalLLMPromptEnhancer
