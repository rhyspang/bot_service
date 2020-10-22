# -*- coding: utf-8 -*-
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

from bot_service.apps.engine.views import train_model, dialog

urlpatterns = [
    path('train/', train_model),
    path('inference/', dialog),
]
