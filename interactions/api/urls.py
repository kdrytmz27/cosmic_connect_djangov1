# interactions/api/urls.py

from django.urls import path
from .views import DiscoverView, DailyMatchView, LikeView

urlpatterns = [
    path('discover/', DiscoverView.as_view(), name='discover'),
    path('daily-match/', DailyMatchView.as_view(), name='daily-match'),
    path('like/<int:user_id>/', LikeView.as_view(), name='like'),
    # Block, SuperLike gibi diğer endpoint'ler buraya eklenebilir.
]