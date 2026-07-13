"""
Research Paper Intelligence Platform
Run: python main.py
"""

import socket
import subprocess
import sys


def find_free_port(start: int = 8501, end: int = 8510) -> int:
    for port in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"No free port found between {start} and {end}.")


def main():
    port = find_free_port()
    print(f"Starting app at http://localhost:{port}")

    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "streamlit_app.py",
            "--server.port",
            str(port),
            "--server.headless",
            "true",
        ],
        check=True,
    )


if __name__ == "__main__":
    main()
