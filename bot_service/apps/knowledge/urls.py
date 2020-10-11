# -*- coding: utf-8 -*-
from django.urls import path, include
from rest_framework_nested import routers

from bot_service.apps.knowledge.views import KnowledgeBaseViewSet
from bot_service.apps.knowledge.views import KnowledgeItemViewSet

router = routers.SimpleRouter()
router.register(r'knowledge_base', KnowledgeBaseViewSet)

knowledge_item_router = routers.NestedDefaultRouter(
    router, r'knowledge_base', lookup='knowledge_base')
knowledge_item_router.register(
    r'knowledge_item', KnowledgeItemViewSet, basename='knowledge_base')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(knowledge_item_router.urls)),
]
