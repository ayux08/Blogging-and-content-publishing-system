"""
URL configuration for Blogverse project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts import views as accounts_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', accounts_views.portal, name='portal'),
    path('accounts/', include('accounts.urls')),
    path('author/', include('author.urls')),
    path('reader/', include('reader.urls')),
    # Admin Zone (custom, not Django admin)
    path('admin_zone/', include('accounts.admin_urls')),
    path('ai/', include('ai.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
