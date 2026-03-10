import os
import sys
import subprocess
import threading

# helper functions that start processes and prefix their output

def _choose_python(service_dir: str) -> str:
    root = os.getcwd()
    python_exec = sys.executable
    if os.name == 'nt':
        candidate = os.path.join(root, service_dir, 'venv', 'Scripts', 'python.exe')
    else:
        candidate = os.path.join(root, service_dir, 'venv', 'bin', 'python')
    if os.path.isfile(candidate):
        python_exec = candidate
    return python_exec


def start_service(service_dir: str, port: int) -> subprocess.Popen:
    root = os.getcwd()
    env = os.environ.copy()
    env['PORT'] = str(port)
    python_exec = _choose_python(service_dir)
    cmd = [python_exec, '-m', f"{service_dir}.app"]

    proc = subprocess.Popen(
        cmd,
        cwd=root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    def _reader():
        prefix = f"[{service_dir}] "
        for line in proc.stdout or []:
            print(prefix + line.rstrip())
    threading.Thread(target=_reader, daemon=True).start()

    return proc

if __name__ == '__main__':
    import argparse
    import time

    parser = argparse.ArgumentParser(description="Start AI-Agent services.")
    parser.add_argument('services', nargs='*', help="List of services to start. If none provided, starts all.")
    args = parser.parse_args()

    # Dictionary of all available services and their ports
    all_services = {
        'main_service': 5000,
        'editor_service': 5001,
        'analyzer_service': 5002,
        'transform_service': 5003,
        'visualization_service': 5004,
        'chat_service': 5005,
        'auth_service': 5006,
        'file_service': 5010,
        'vector_service': 5020,
    }

    services_to_start = args.services if args.services else list(all_services.keys())

    # Validate requested services
    for service_name in services_to_start:
        if service_name not in all_services:
            print(f"Error: Unknown service '{service_name}'.")
            print(f"Available services: {', '.join(all_services.keys())}")
            sys.exit(1)

    processes = []
    print(f"Starting services: {', '.join(services_to_start)}")
    for service_dir in services_to_start:
        port = all_services[service_dir]
        p = start_service(service_dir, port)
        processes.append((service_dir, p))
    
    try:
        # Wait for all processes
        for service_dir, p in processes:
            p.wait()
    except KeyboardInterrupt:
        print("\nShutting down all services...")
        for service_dir, p in processes:
            print(f"Stopping {service_dir}...")
            p.terminate()
        for service_dir, p in processes:
            p.wait()
        print("All services stopped.")