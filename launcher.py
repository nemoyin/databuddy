"""JWBuddy 服务启动器 — 启动所有服务并验证"""
import os
import sys
import subprocess
import time
import urllib.request

BACKEND = r"E:\mysql\AI智能体\jwbuddy\backend"
DESKTOP = r"E:\mysql\AI智能体\jwbuddy\desktop"
PYTHON = os.path.join(BACKEND, ".venv", "Scripts", "python.exe")


def log(msg):
    print(f"[JWB] {msg}")


def kill_port(port):
    try:
        result = subprocess.run(["netstat", "-ano"], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if f":{port}" in line and "LISTENING" in line:
                parts = line.strip().split()
                pid = parts[-1]
                if pid.isdigit():
                    subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
                    log(f"killed PID {pid} on port {port}")
    except Exception:
        pass


def wait_for_port(port, health_path, timeout=12):
    for i in range(timeout):
        try:
            r = urllib.request.urlopen(f"http://localhost:{port}{health_path}", timeout=2)
            if r.status == 200:
                return r.read().decode()
        except Exception:
            pass
        time.sleep(1)
    return None


def start_service(name, cmd, port, health_path="/health"):
    log(f"Starting {name} on port {port}...")
    kill_port(port)
    subprocess.Popen(
        cmd,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
        close_fds=True,
    )
    body = wait_for_port(port, health_path)
    if body is not None:
        log(f"  [OK] {name}: {body[:80]}")
        return True
    else:
        log(f"  [FAIL] {name} timed out")
        return False


def main():
    log("=" * 40)
    log("JWBuddy 服务启动器")
    log("=" * 40)

    ok = start_service(
        "Backend API",
        [PYTHON, os.path.join(BACKEND, "run_server.py")],
        port=8000,
    )
    if not ok:
        log("Backend failed, aborting")
        return

    start_service(
        "Web Frontend",
        [sys.executable, "-m", "http.server", "8080", "-d", os.path.join(DESKTOP, "dist")],
        port=8080,
        health_path="/index.html",
    )

    start_service(
        "MCP Server",
        [PYTHON, os.path.join(BACKEND, "mcp_server.py")],
        port=8001,
    )

    log("=" * 40)
    log("All services started!")
    log(f"  Web UI:   http://localhost:8080/")
    log(f"  API:      http://localhost:8000/health")
    log(f"  MCP:      http://localhost:8001/health")
    log(f"  Swagger:  http://localhost:8000/docs")
    log("=" * 40)


if __name__ == "__main__":
    main()
