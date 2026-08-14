import os
import sys
from pathlib import Path

# Add project root to sys.path so Django can locate apps and config
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from django.core.wsgi import get_wsgi_application

# Vercel looks for 'app' or 'application' as the entrypoint callable
application = get_wsgi_application()
app = application