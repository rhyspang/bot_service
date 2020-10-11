# Create your views here.

# ViewSets define the view behavior.
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from knowledge.models import KnowledgeBase
from knowledge.models import KnowledgeItem
from knowledge.serializers import KnowledgeBaseSerializer
from knowledge.serializers import KnowledgeItemSerializer


class KnowledgeBaseViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = KnowledgeBase.objects.all()
    serializer_class = KnowledgeBaseSerializer

    @action(methods=['put'], detail=True, url_path='update_users',
            url_name='update_users')
    def update_users(self):
        pass


class KnowledgeItemViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)

    # queryset = KnowledgeItem.objects.all()
    serializer_class = KnowledgeItemSerializer

    def get_queryset(self):
        return KnowledgeItem.objects.filter(
            knowledge_base=self.kwargs['knowledge_base_pk'])
