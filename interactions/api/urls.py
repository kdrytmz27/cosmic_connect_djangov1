from django.urls import path
from .views import (
    DiscoverProfilesView,
    LikeProfileView,
    PassProfileView,
    ActivityDataView,
    DailyMatchView,
)

urlpatterns = [
    path('discover/', DiscoverProfilesView.as_view(), name='discover-profiles'),
    path('like/<int:user_id>/', LikeProfileView.as_view(), name='like-profile'),
    path('pass/<int:user_id>/', PassProfileView.as_view(), name='pass-profile'),
    
    # GÜNCELLENDİ: Yeni endpointleri ekledik
    path('activity/', ActivityDataView.as_view(), name='activity-data'),
    path('daily-match/', DailyMatchView.as_view(), name='daily-match'),
]