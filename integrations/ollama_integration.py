import requests
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass
from utils.logger import log_llm_interaction


@dataclass
class OllamaModel:
    """Ollama 모델 정보"""

    name: str
    size: str
    modified_at: str
    digest: str


class OllamaClient:
    def __init__(self, host: str = "http://localhost:11434"):
        self.host = host.rstrip("/")
        self._connected = False
        self._available_models: List[OllamaModel] = []

    def test_connection(self) -> Tuple[bool, str]:
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            if response.status_code == 200:
                self._connected = True
                self._load_models(response.json())
                return (
                    True,
                    f"✅ Ollama 서버 연결 성공! ({len(self._available_models)}개 모델 발견)",
                )
            else:
                return False, f"❌ 서버 응답 오류: {response.status_code}"
        except requests.exceptions.ConnectionError:
            return (
                False,
                "❌ Ollama 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.",
            )
        except requests.exceptions.Timeout:
            return False, "❌ 연결 시간 초과. 서버 상태를 확인하세요."
        except Exception as e:
            return False, f"❌ 연결 오류: {str(e)}"

    def _load_models(self, response_data: dict):
        self._available_models = []
        models = response_data.get("models", [])

        for model in models:
            self._available_models.append(
                OllamaModel(
                    name=model.get("name", "unknown"),
                    size=self._format_size(model.get("size", 0)),
                    modified_at=model.get("modified_at", ""),
                    digest=model.get("digest", "")[:12],
                )
            )

    def _format_size(self, size_bytes: int) -> str:
        if size_bytes == 0:
            return "Unknown"

        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def available_models(self) -> List[OllamaModel]:
        return self._available_models

    def get_model_names(self) -> List[str]:
        return [model.name for model in self._available_models]

    def get_model_info_display(self) -> List[Dict]:
        return [
            {
                "이름": model.name,
                "크기": model.size,
                "수정일": model.modified_at[:10] if model.modified_at else "N/A",
            }
            for model in self._available_models
        ]

    def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Dict:
        if not self._connected:
            raise ConnectionError("Ollama 서버에 연결되어 있지 않습니다.")

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }

        try:
            response = requests.post(f"{self.host}/api/chat", json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()

            # 응답 및 토큰 정보 로깅
            content = result.get("message", {}).get("content", "")
            tokens = None
            if "eval_count" in result:
                tokens = {
                    "input": result.get("prompt_eval_count", 0),
                    "output": result.get("eval_count", 0),
                    "total": result.get("prompt_eval_count", 0)
                    + result.get("eval_count", 0),
                }
            log_llm_interaction("Ollama", model, messages, content, tokens)

            return result
        except requests.exceptions.Timeout:
            raise TimeoutError(
                "응답 시간 초과. 더 작은 모델을 사용하거나 요청을 단순화하세요."
            )
        except Exception as e:
            raise RuntimeError(f"Ollama 요청 실패: {str(e)}")

    def generate(
        self, model: str, prompt: str, temperature: float = 0.7, max_tokens: int = 1024
    ) -> str:
        if not self._connected:
            raise ConnectionError("Ollama 서버에 연결되어 있지 않습니다.")

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }

        try:
            response = requests.post(
                f"{self.host}/api/generate", json=payload, timeout=60
            )
            response.raise_for_status()

            result = response.json()
            content = result.get("response", "")

            tokens = None
            if "eval_count" in result:
                tokens = {
                    "input": result.get("prompt_eval_count", 0),
                    "output": result.get("eval_count", 0),
                    "total": result.get("prompt_eval_count", 0)
                    + result.get("eval_count", 0),
                }

            # messages 형식으로 변환하여 로깅
            messages = [{"role": "user", "content": prompt}]
            log_llm_interaction("Ollama", model, messages, content, tokens)

            return content
        except Exception as e:
            raise RuntimeError(f"Ollama 생성 실패: {str(e)}")


class PromptEnhancer:
    ENHANCEMENT_SYSTEM_PROMPT = """You are an expert prompt engineer for photorealistic AI image generation models like Stable Diffusion and Flux.

Your role is to enhance image generation prompts to be:
1. More natural and flowing in English
2. More detailed and specific
3. Better structured for optimal model interpretation
4. Consistent in style and tone

Rules:
- Keep the enhanced prompt concise but detailed
- Maintain all key elements from the original
- Use professional photography terminology
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

    def __init__(self, ollama_client: OllamaClient):
        self.client = ollama_client
        self.default_model = None

    def set_default_model(self, model_name: str):
        """기본 모델 설정"""
        self.default_model = model_name

    def enhance_prompt(
        self,
        original_prompt: str,
        model: Optional[str] = None,
        user_requirements: Optional[str] = None,
    ) -> str:
        model = model or self.default_model
        if not model:
            raise ValueError("모델이 지정되지 않았습니다.")

        user_content = f"Enhance this prompt:\n{original_prompt}"
        if user_requirements:
            user_content += f"\n\nAdditional requirements: {user_requirements}"

        try:
            response = self.client.chat(
                model=model,
                messages=[
                    {"role": "system", "content": self.ENHANCEMENT_SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                ],
                temperature=0.7,
            )
            return response["message"]["content"].strip()
        except Exception as e:
            print(f"Enhancement failed: {e}")
            return original_prompt

    def translate_to_korean(
        self, english_prompt: str, model: Optional[str] = None
    ) -> str:
        model = model or self.default_model
        if not model:
            raise ValueError("모델이 지정되지 않았습니다.")

        try:
            response = self.client.chat(
                model=model,
                messages=[
                    {"role": "system", "content": self.TRANSLATION_SYSTEM_PROMPT},
                    {"role": "user", "content": english_prompt},
                ],
                temperature=0.3,  # 번역은 낮은 온도로
            )
            return response["message"]["content"].strip()
        except Exception as e:
            print(f"Translation failed: {e}")
            return "번역 실패"


# 싱글톤 클라이언트 인스턴스
_ollama_client: Optional[OllamaClient] = None


def get_ollama_client(host: str = "http://localhost:11434") -> OllamaClient:
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient(host)
    return _ollama_client


def reset_ollama_client():
    global _ollama_client
    _ollama_client = None
