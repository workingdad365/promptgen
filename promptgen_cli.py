"""promptgen 콘솔 스크립트 진입점."""

import os
import signal
import sys
from pathlib import Path


def _install_force_quit() -> None:
    """Streamlit 종료가 멈출 때를 대비해 두 번째 Ctrl+C를 강제 종료로 처리함.

    Streamlit이 bootstrap 단계에서 자체 SIGINT 핸들러를 등록하므로,
    signal.signal 을 감싸 해당 핸들러에 강제 종료 경로를 덧붙임.
    """
    original_signal = signal.signal
    interrupt_count = 0

    def patched_signal(signalnum, handler):
        if signalnum == signal.SIGINT and callable(handler):
            inner = handler

            def wrapper(sig, frame):
                nonlocal interrupt_count
                interrupt_count += 1
                if interrupt_count >= 2:
                    print("\n강제 종료합니다.", file=sys.stderr, flush=True)
                    os._exit(1)
                print(
                    "종료 중... 응답이 없으면 Ctrl+C를 한 번 더 누르세요.",
                    file=sys.stderr,
                    flush=True,
                )
                return inner(sig, frame)

            handler = wrapper
        return original_signal(signalnum, handler)

    signal.signal = patched_signal


# Windows의 Hyper-V/WinNAT 예약 포트(8085~9003 등)와 동적 포트 범위를 피하기 위한 기본값.
DEFAULT_PORT = 28501


def main() -> int:
    from streamlit.web import cli as stcli

    _install_force_quit()
    app_path = Path(__file__).resolve().parent / "app.py"
    user_args = sys.argv[1:]

    port_args: list[str] = []
    if not any(arg.split("=")[0] == "--server.port" for arg in user_args):
        if not os.environ.get("STREAMLIT_SERVER_PORT"):
            port_args = ["--server.port", str(DEFAULT_PORT)]

    sys.argv = ["streamlit", "run", str(app_path), *port_args, *user_args]
    return stcli.main()


if __name__ == "__main__":
    sys.exit(main())
