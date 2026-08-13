"""Dynamic Prompts 와일드카드(__name__) 치환 유틸.

지정된 디렉토리(서브디렉토리 제외)에서 `<name>.txt` 를 찾아 임의의 한 줄로 치환함.
"""

import random
import re
from pathlib import Path
from typing import List, Optional, Tuple

# __hair__ 형태만 인식. 경로 구분자는 허용하지 않음(서브디렉토리 미지원 + 경로 탈출 방지).
WILDCARD_PATTERN = re.compile(r"__([A-Za-z0-9가-힣 _\-]+?)__")


def resolve_directory(directory: Optional[str]) -> Optional[Path]:
    """유효한 디렉토리면 Path 반환, 아니면 None."""
    if not directory or not str(directory).strip():
        return None
    try:
        path = Path(str(directory).strip()).expanduser()
        return path if path.is_dir() else None
    except OSError:
        return None


def list_wildcards(directory: Optional[str]) -> List[str]:
    """디렉토리에 존재하는 와일드카드 이름 목록(확장자 제외)."""
    base = resolve_directory(directory)
    if base is None:
        return []
    try:
        return sorted(p.stem for p in base.glob("*.txt") if p.is_file())
    except OSError:
        return []


def _find_file(base: Path, name: str) -> Optional[Path]:
    candidate = base / f"{name}.txt"
    try:
        if candidate.is_file():
            return candidate
        lowered = name.lower()
        for path in base.glob("*.txt"):
            if path.is_file() and path.stem.lower() == lowered:
                return path
    except OSError:
        return None
    return None


def _read_choices(path: Path) -> List[str]:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError:
        return []
    return [
        line.strip()
        for line in lines
        if line.strip() and not line.strip().startswith("#")
    ]


def expand_wildcards(
    text: Optional[str], directory: Optional[str]
) -> Tuple[str, List[str]]:
    """텍스트 내 `__name__` 을 파일에서 뽑은 임의의 한 줄로 치환.

    Returns:
        (치환된 텍스트, 처리 로그 목록)
    """
    if not text or "__" not in text:
        return text or "", []

    base = resolve_directory(directory)
    if base is None:
        return text, []

    logs: List[str] = []

    def _replace(match: re.Match) -> str:
        name = match.group(1).strip()
        if not name:
            return match.group(0)
        path = _find_file(base, name)
        if path is None:
            logs.append(f"__{name}__ → 파일 없음 ({name}.txt)")
            return match.group(0)
        choices = _read_choices(path)
        if not choices:
            logs.append(f"__{name}__ → 내용 없음 ({path.name})")
            return match.group(0)
        picked = random.choice(choices)
        logs.append(f"__{name}__ → {picked}")
        return picked

    return WILDCARD_PATTERN.sub(_replace, text), logs
