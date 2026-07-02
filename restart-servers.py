import subprocess
import time
import psutil

# Kill processes on ports 8000 and 3003
for conn in psutil.net_connections():
    if conn.laddr.port in [8000, 3003]:
        try:
            process = psutil.Process(conn.pid)
            print(f"Killing process {conn.pid} on port {conn.laddr.port}")
            process.terminate()
            time.sleep(0.5)
            if process.is_running():
                process.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

print("Waiting for ports to be released...")
time.sleep(2)

print("Servers stopped. Please start them manually:")
print("  Backend: cd backend && python -m uvicorn app.main:app --reload --port 8000")
print("  Frontend: cd frontend && npm run dev")
