from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('users/', views.admin_users, name='admin_users'),
    path('users/toggle/<int:user_id>/', views.admin_toggle_user, name='admin_toggle_user'),
    path('users/delete/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
    path('categories/', views.admin_categories, name='admin_categories'),
    path('categories/delete/<int:cat_id>/', views.admin_delete_category, name='admin_delete_category'),
    path('tags/', views.admin_tags, name='admin_tags'),
    path('tags/delete/<int:tag_id>/', views.admin_delete_tag, name='admin_delete_tag'),
    path('posts/', views.admin_posts, name='admin_posts'),
    path('comments/', views.admin_comments, name='admin_comments'),
    path('media/', views.admin_media, name='admin_media'),
    path('media/delete/<int:media_id>/', views.admin_delete_media, name='admin_delete_media'),
    path('analytics/', views.admin_analytics, name='admin_analytics'),
]
