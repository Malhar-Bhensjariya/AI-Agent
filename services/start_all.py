import multiprocessing
import os
import sys

def run_service(service_dir, port):
    os.chdir(service_dir)
    os.environ['PORT'] = str(port)
    os.execv(sys.executable, [sys.executable, 'app.py'])

if __name__ == '__main__':
    services = [
        ('main_service', 5000),
        ('editor_service', 5001),
        ('analyzer_service', 5002),
        ('transform_service', 5003),
        ('visualization_service', 5004),
        ('chat_service', 5005),
        ('auth_service', 5006)
    ]
    
    processes = []
    for service_dir, port in services:
        p = multiprocessing.Process(target=run_service, args=(service_dir, port))
        p.start()
        processes.append(p)
    
    for p in processes:
        p.join()