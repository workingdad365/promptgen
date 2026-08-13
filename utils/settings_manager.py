"""사용자 설정(엔진 옵션, 최근 선택 모델 등) 영속화."""

import json
import os
from pathlib import Path
from typing import Any, Dict

SETTINGS_FILE = Path(__file__).resolve().parent.parent / "user_settings.json"

# 저장 대상 키와 기본값. 여기에 없는 키는 저장/복원하지 않음.
DEFAULT_SETTINGS: Dict[str, Any] = {
    "mode": "sfw",
    "style": "photorealistic",
    "prompt_target": "legacy",
    "use_modifiers": True,
    "use_quality_prefix": True,
    "use_natural_photo": True,
    "natural_directive_keys": None,  # None이면 전체 지시문 사용
    "last_external_model": None,
    "ollama_host": "http://localhost:11434",
    "last_ollama_model": None,
    "save_history": True,
    "last_user_requirements": "",
    "category_selections": {},
}


def _load() -> Dict[str, Any]:
    if not SETTINGS_FILE.exists():
        return {}
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _save(data: Dict[str, Any]) -> None:
    try:
        tmp = SETTINGS_FILE.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, SETTINGS_FILE)
    except OSError as e:
        print(f"설정 저장 실패: {e}")


def load_settings() -> Dict[str, Any]:
    """기본값에 저장된 값을 병합한 설정 반환."""
    merged = dict(DEFAULT_SETTINGS)
    for key, value in _load().items():
        if key in DEFAULT_SETTINGS:
            merged[key] = value
    return merged


def save_settings(updates: Dict[str, Any]) -> None:
    """알려진 키만 병합 저장. 변경분이 없으면 파일을 건드리지 않음."""
    data = _load()
    changed = False
    sentinel = object()
    for key, value in updates.items():
        if key not in DEFAULT_SETTINGS:
            continue
        if data.get(key, sentinel) != value:
            data[key] = value
            changed = True
    if changed:
        _save(data)
