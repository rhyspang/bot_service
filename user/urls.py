# -*- coding: utf-8 -*-
from django.urls import path, include
from rest_framework import routers

from user.views import UserViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
