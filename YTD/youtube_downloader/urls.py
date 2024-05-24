from django.urls import path
from . import views

urlpatterns = [
    path('video-download', views.DownloadView.as_view(), name='download_video'),
]
