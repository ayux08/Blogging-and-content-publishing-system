from django.urls import path
from . import views

urlpatterns = [
    path("index/", views.index, name="ai_index"),
    path("summarize/", views.summarize, name="ai_summarize"),
    path("translate/", views.translate, name="ai_translate"),
    path("api/summarize/", views.api_summarize, name="ai_api_summarize"),
    path("api/translate/", views.api_translate, name="ai_api_translate"),
]
