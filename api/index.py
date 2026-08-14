# api/index.py
import os
import sys
from pathlib import Path
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = get_wsgi_application()

# Run migrations once on startup if running on Vercel with temp DB
if os.environ.get('VERCEL'):
    try:
        call_command('migrate', interactive=False)
    except Exception as e:
        print("Migration error:", e)