from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='reader_dashboard'),
    path('browse/', views.browse, name='reader_browse'),
    path('blog/<int:post_id>/', views.blog_view, name='reader_blog'),
    path('ajax/like/<int:post_id>/', views.ajax_like, name='ajax_like'),
    path('ajax/bookmark/<int:post_id>/', views.ajax_bookmark, name='ajax_bookmark'),
    path('ajax/share/<int:post_id>/', views.ajax_share, name='ajax_share'),
    path('notifications/', views.notifications, name='reader_notifications'),
    path('notifications/read/<int:notif_id>/', views.mark_notification_read, name='mark_notif_read'),
    path('notifications/read-all/', views.mark_all_read, name='mark_all_read'),
    path('bookmarks/', views.bookmarks, name='reader_bookmarks'),
    path('liked/', views.liked_posts, name='reader_liked_posts'),
    path('history/', views.history, name='reader_history'),
    path('profile/', views.profile, name='reader_profile'),
    path('user/<str:username>/', views.public_profile, name='public_profile'),
    path('upgrade-to-author/', views.upgrade_to_author, name='upgrade_to_author'),
    path('ajax/follow/<int:user_id>/', views.ajax_follow, name='ajax_follow'),
]
