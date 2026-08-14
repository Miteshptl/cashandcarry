import os
from django.core.wsgi import get_wsgi_application

# Point to your project's settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Vercel looks for a variable named 'app'
app = get_wsgi_application()