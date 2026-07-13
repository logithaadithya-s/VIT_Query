#!/usr/bin/env python3
"""Start both the FastAPI backend and Next.js frontend."""

import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def find_free_port(start: int = 8000, end: int = 8010) -> int:
    for port in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError("No free port found for backend.")


def main():
    api_port = find_free_port(8000, 8010)

    env = os.environ.copy()
    env["NEXT_PUBLIC_API_URL"] = f"http://localhost:{api_port}"

    print(f"\n  ResearchIQ Platform")
    print(f"  ─────────────────────────────────")
    print(f"  Backend API:  http://localhost:{api_port}")
    print(f"  Frontend UI:  http://localhost:3000")
    print(f"  ─────────────────────────────────\n")

    backend = subprocess.Popen(
        [
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", "127.0.0.1",
            "--port", str(api_port),
        ],
        cwd=ROOT,
    )

    time.sleep(1.5)

    frontend = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=ROOT / "frontend",
        env=env,
    )

    def shutdown(*_):
        backend.terminate()
        frontend.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    frontend.wait()


if __name__ == "__main__":
    main()
