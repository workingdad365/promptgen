"""사용자 설정(최근 선택 모델 등) 영속화."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

SETTINGS_FILE = Path(__file__).resolve().parent.parent / "user_settings.json"


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


def get_last_external_model() -> Optional[str]:
    value = _load().get("last_external_model")
    return value if isinstance(value, str) and value else None


def set_last_external_model(model: str) -> None:
    data = _load()
    if data.get("last_external_model") == model:
        return
    data["last_external_model"] = model
    _save(data)
