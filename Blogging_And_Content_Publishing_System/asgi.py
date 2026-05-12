"""
ASGI config for Blogging and Content Publishing System.
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Blogging_And_Content_Publishing_System.settings')
application = get_asgi_application()
