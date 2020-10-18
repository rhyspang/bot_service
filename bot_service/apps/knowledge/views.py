# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from bot_service.apps.knowledge.models import KnowledgeBase
from bot_service.apps.knowledge.models import KnowledgeItem
from bot_service.apps.knowledge.serializers import KnowledgeBaseSerializer
from bot_service.apps.knowledge.serializers import KnowledgeItemSerializer
from bot_service.base_views import BaseViewSet
from bot_service.response.service_response import ServiceResponse as Response


class KnowledgeBaseViewSet(BaseViewSet):
    permission_classes = (IsAuthenticated,)
    # queryset = KnowledgeBase.objects.all()
    serializer_class = KnowledgeBaseSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('name', 'shop_id', 'desc')

    def get_queryset(self):
        if self.request.user.is_staff:
            return KnowledgeBase.objects.all()
        else:
            return self.request.user.knowledge_base_set.all()

    @action(methods=['post'], detail=True, url_path='update_users',
            url_name='update_users')
    def update_users(self, request, pk, **kwargs):
        user_id_list = request.data.get('users', [])
        instance = self.get_object()
        instance.users.clear()
        for user_id in user_id_list:
            user = User.objects.get(pk=int(user_id))
            instance.users.add(user)
        instance.save()
        return Response(data=user_id_list)


class KnowledgeItemViewSet(BaseViewSet):
    permission_classes = (IsAuthenticated,)

    # queryset = KnowledgeItem.objects.all()
    serializer_class = KnowledgeItemSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('question', )

    def get_queryset(self):
        return KnowledgeItem.objects.filter(
            knowledge_base=self.kwargs['knowledge_base_pk'])
