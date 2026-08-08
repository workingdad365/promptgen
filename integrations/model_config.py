"""models.json 기반 외부 LLM 모델 설정 로더."""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

MODELS_FILE = Path(__file__).resolve().parent.parent / "models.json"

SUPPORTED_PROVIDERS = {"openai", "gemini", "anthropic", "openai_compat"}

PROVIDER_LABELS = {
    "openai": "OpenAI",
    "gemini": "Google Gemini",
    "anthropic": "Anthropic Claude",
    "openai_compat": "OpenAI 호환",
}


@dataclass(frozen=True)
class ModelConfig:
    provider: str
    model: str
    api_key_env: str
    base_url: Optional[str] = None

    @property
    def api_key(self) -> Optional[str]:
        return os.getenv(self.api_key_env)

    @property
    def provider_label(self) -> str:
        return PROVIDER_LABELS.get(self.provider, self.provider)


class ModelConfigError(Exception):
    pass


_cache: Optional[List[ModelConfig]] = None


def _normalize_base_url(base_url: Optional[str]) -> Optional[str]:
    if not base_url:
        return None
    # OpenAI SDK 는 엔드포인트 경로를 스스로 붙이므로 루트 URL 만 남김
    return base_url.rstrip("/").removesuffix("/chat/completions") or None


def _parse(raw: object) -> List[ModelConfig]:
    if not isinstance(raw, list):
        raise ModelConfigError("models.json 의 최상위는 배열이어야 합니다.")

    configs: List[ModelConfig] = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ModelConfigError(f"models.json[{index}] 항목이 객체가 아닙니다.")

        provider = str(item.get("provider", "")).strip()
        model = str(item.get("model", "")).strip()
        api_key_env = str(item.get("api_key", "")).strip()

        if not provider or not model or not api_key_env:
            raise ModelConfigError(
                f"models.json[{index}] 에 provider/model/api_key 값이 모두 필요합니다."
            )
        if provider not in SUPPORTED_PROVIDERS:
            raise ModelConfigError(
                f"models.json[{index}] 의 provider '{provider}' 는 지원되지 않습니다. "
                f"지원: {', '.join(sorted(SUPPORTED_PROVIDERS))}"
            )

        base_url = _normalize_base_url(item.get("base_url"))
        if provider == "openai_compat" and not base_url:
            raise ModelConfigError(
                f"models.json[{index}] 의 provider 'openai_compat' 는 base_url 이 필요합니다."
            )

        configs.append(
            ModelConfig(
                provider=provider,
                model=model,
                api_key_env=api_key_env,
                base_url=base_url,
            )
        )

    if not configs:
        raise ModelConfigError("models.json 에 등록된 모델이 없습니다.")

    return configs


def load_models(force_reload: bool = False) -> List[ModelConfig]:
    global _cache
    if _cache is not None and not force_reload:
        return _cache

    if not MODELS_FILE.exists():
        raise ModelConfigError(f"모델 설정 파일을 찾을 수 없습니다: {MODELS_FILE}")

    try:
        with open(MODELS_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except json.JSONDecodeError as e:
        raise ModelConfigError(f"models.json 파싱 실패: {e}") from e

    _cache = _parse(raw)
    return _cache


def get_model_names() -> List[str]:
    return [c.model for c in load_models()]


def get_model_config(model: str) -> Optional[ModelConfig]:
    for config in load_models():
        if config.model == model:
            return config
    return None


def get_default_model() -> str:
    return load_models()[0].model


def get_provider_map() -> Dict[str, str]:
    return {c.model: c.provider for c in load_models()}
