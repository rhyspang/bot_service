# -*- coding: utf-8 -*-
from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

from bot_service.apps.user.views import UserViewSet, get_user_info, \
    FormatTokenObtainPairView, logout

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('user/info/', get_user_info),
    path('user/logout/', logout),
    path('token/', FormatTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
