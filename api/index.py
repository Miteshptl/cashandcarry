import os
import sys
from pathlib import Path
from django.core.wsgi import get_wsgi_application

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = get_wsgi_application()