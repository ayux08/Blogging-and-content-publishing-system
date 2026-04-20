from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='author_dashboard'),
    path('create/', views.create_post, name='author_create'),
    path('edit/<int:post_id>/', views.edit_post, name='author_edit'),
    path('delete/<int:post_id>/', views.delete_post, name='author_delete'),
    path('publish-draft/<int:post_id>/', views.publish_draft, name='author_publish_draft'),
    path('delete-image/<int:image_id>/', views.delete_post_image, name='author_delete_image'),
    path('drafts/', views.drafts, name='author_drafts'),
    path('posts/', views.my_posts, name='author_posts'),
    path('status/', views.post_status, name='author_status'),
    path('media/', views.media_upload, name='author_media'),
    path('comments/', views.comments, name='author_comments'),
    path('comment/reply/<int:comment_id>/', views.reply_comment, name='author_reply_comment'),
    path('profile/', views.author_profile, name='author_profile'),
]
