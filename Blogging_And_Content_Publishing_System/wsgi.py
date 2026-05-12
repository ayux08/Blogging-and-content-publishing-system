"""
WSGI config for Blogging and Content Publishing System.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Blogging_And_Content_Publishing_System.settings')
application = get_wsgi_application()
