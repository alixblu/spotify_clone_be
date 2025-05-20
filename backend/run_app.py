import subprocess
import sys
import os
import time
from threading import Thread

def run_django():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    subprocess.run([sys.executable, 'manage.py', 'runserver', '0.0.0.0:8000'])

def run_daphne():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    # Use python -m daphne to ensure proper Python path
    subprocess.run([
        sys.executable, 
        '-m', 
        'daphne',
        '-b', '0.0.0.0',
        '-p', '8001',
        'backend.asgi:application'
    ])

if __name__ == '__main__':
    # Start Django server
    django_thread = Thread(target=run_django)
    django_thread.daemon = True
    django_thread.start()

    # Give Django server a moment to start
    time.sleep(2)

    # Start Daphne server
    daphne_thread = Thread(target=run_daphne)
    daphne_thread.daemon = True
    daphne_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        sys.exit(0)