import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    from django.core.wsgi import get_wsgi_application
    app = get_wsgi_application()
except Exception as e:
    import traceback
    print("DJANGO INIT ERROR:", traceback.format_exc())
    raise e