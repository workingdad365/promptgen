import sys
from datetime import datetime
from typing import List, Dict, Optional


def log_llm_interaction(
    provider: str,
    model: str,
    messages: List[Dict[str, str]],
    response: str,
    tokens: Optional[Dict[str, int]] = None,
):
    """
    LLM 상호작용 로그를 콘솔에 출력합니다.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 구분선 및 헤더
    print(f"\n{'=' * 60}")
    print(f"[{timestamp}] 🤖 LLM Interaction Log")
    print(f"Provider: {provider}")
    print(f"Model:    {model}")
    print(f"{'-' * 60}")

    # 입력 메시지 출력
    print("📥 [Input Messages]")
    for i, msg in enumerate(messages):
        role = msg.get("role", "unknown").upper()
        content = msg.get("content", "")
        # 시스템 프롬프트 등 너무 긴 내용은 일부 생략 가능하지만,
        # 사용자가 디테일한 정보를 원했으므로 전체 출력 혹은 적절히 포맷팅
        print(f"  [{i + 1}] {role}:")
        # 줄바꿈이 있는 경우 들여쓰기 처리
        for line in content.splitlines():
            print(f"      {line}")

    print(f"{'-' * 60}")

    # 출력 메시지 출력
    print("📤 [Output Response]")
    for line in response.splitlines():
        print(f"  {line}")

    # 토큰 정보 출력 (있는 경우)
    if tokens:
        print(f"{'-' * 60}")
        print("📊 [Token Usage]")
        input_tokens = tokens.get("input", "N/A")
        output_tokens = tokens.get("output", "N/A")
        total_tokens = tokens.get("total", "N/A")
        print(
            f"  Input: {input_tokens} | Output: {output_tokens} | Total: {total_tokens}"
        )

    print(f"{'=' * 60}\n")
    sys.stdout.flush()
