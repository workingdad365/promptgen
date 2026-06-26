import os
from typing import Optional, Tuple
from utils.logger import log_llm_interaction

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


# 지원되는 모델 목록 (첫 번째가 기본값)
EXTERNAL_LLM_MODELS = ["gpt-5.4-mini", "gemini-3.5-flash", "claude-haiku-4-5"]


def get_provider_from_model(model: str) -> str:
    """모델명에서 제공자 판별"""
    if model.startswith("gpt"):
        return "openai"
    elif model.startswith("gemini"):
        return "gemini"
    elif model.startswith("claude"):
        return "anthropic"
    return "unknown"


def check_api_key_for_model(model: str) -> Tuple[bool, str]:
    """모델에 맞는 API 키 확인"""
    provider = get_provider_from_model(model)

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            return True, "OPENAI_API_KEY 확인됨"
        return False, "OPENAI_API_KEY 환경변수가 설정되지 않았습니다."

    elif provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            return True, "GEMINI_API_KEY 확인됨"
        return False, "GEMINI_API_KEY 환경변수가 설정되지 않았습니다."

    elif provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            return True, "ANTHROPIC_API_KEY 확인됨"
        return False, "ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다."

    return False, f"알 수 없는 모델: {model}"


class ExternalLLMClient:
    """
    외부 LLM API 통합 클라이언트

    모델명에 따라 OpenAI, Gemini, Claude API 자동 선택
    """

    def __init__(self, model: str = "gpt-5.4-mini"):
        """
        Args:
            model: 사용할 모델명
        """
        self.model = model
        self.provider = get_provider_from_model(model)
        self._client = None
        self._connected = False

    def test_connection(self) -> Tuple[bool, str]:
        """
        API 연결 테스트

        Returns:
            (연결 성공 여부, 메시지)
        """
        if self.provider == "openai":
            return self._test_openai()
        elif self.provider == "gemini":
            return self._test_gemini()
        elif self.provider == "anthropic":
            return self._test_anthropic()

        return False, f"❌ 알 수 없는 제공자: {self.provider}"

    def _test_openai(self) -> Tuple[bool, str]:
        """OpenAI 연결 테스트"""
        if not OPENAI_AVAILABLE:
            return (
                False,
                "❌ openai 패키지가 설치되어 있지 않습니다. pip install openai 실행 필요",
            )

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return False, "❌ OPENAI_API_KEY 환경변수가 설정되지 않았습니다."

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

    def _test_gemini(self) -> Tuple[bool, str]:
        """Gemini 연결 테스트"""
        if not GEMINI_AVAILABLE:
            return (
                False,
                "❌ google-genai 패키지가 설치되어 있지 않습니다. pip install google-genai 실행 필요",
            )

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return False, "❌ GEMINI_API_KEY 환경변수가 설정되지 않았습니다."

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

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return False, "❌ ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다."

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

        raise RuntimeError(f"알 수 없는 제공자: {self.provider}")

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

            content = response.choices[0].message.content

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

    ENHANCEMENT_SYSTEM_PROMPT_TEMPLATE = """You are an expert prompt engineer for {style_desc} AI image generation models like Stable Diffusion and Flux.
 
 Your role is to enhance image generation prompts to be:
 1. More natural and flowing in English
 2. More detailed and specific
 3. Better structured for optimal model interpretation
 4. Consistent in style and tone
 
 Rules:
 - Keep the enhanced prompt concise but detailed
 - Maintain all key elements from the original
 - Use professional {term_type} terminology
 - Ensure natural language flow
 - DO NOT add explanations, just return the enhanced prompt
 - DO NOT change the core subject or theme"""

    TRANSLATION_SYSTEM_PROMPT = """You are a professional translator specializing in creative and technical content.

Translate the given image generation prompt from English to Korean.

Rules:
- Maintain all technical photography terms
- Keep the natural flow of the description
- Preserve the artistic intent
- DO NOT add explanations
- Return ONLY the Korean translation"""

    def __init__(self, client: ExternalLLMClient):
        self.client = client

    def enhance_prompt(
        self, original_prompt: str, user_requirements: Optional[str] = None, style: str = "photorealistic"
    ) -> str:
        """프롬프트 개선"""
        user_content = f"Enhance this prompt:\n{original_prompt}"
        if user_requirements:
            user_content += f"\n\nAdditional requirements: {user_requirements}"

        style_desc = "photorealistic" if style == "photorealistic" else "high-quality anime style"
        term_type = "photography" if style == "photorealistic" else "anime art"
        system_prompt = self.ENHANCEMENT_SYSTEM_PROMPT_TEMPLATE.format(style_desc=style_desc, term_type=term_type)

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
                    {"role": "system", "content": self.TRANSLATION_SYSTEM_PROMPT},
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
check_openai_api_key = lambda: check_api_key_for_model("gpt-5.4-mini")
