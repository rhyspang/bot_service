# Create your views here.

# ViewSets define the view behavior.
from rest_framework import viewsets

from knowledge.models import KnowledgeBase
from knowledge.models import KnowledgeItem
from knowledge.serializers import KnowledgeBaseSerializer
from knowledge.serializers import KnowledgeItemSerializer


class KnowledgeBaseViewSet(viewsets.ModelViewSet):
    queryset = KnowledgeBase.objects.all()
    serializer_class = KnowledgeBaseSerializer


class KnowledgeItemViewSet(viewsets.ModelViewSet):

    # queryset = KnowledgeItem.objects.all()
    serializer_class = KnowledgeItemSerializer

    def get_queryset(self):
        return KnowledgeItem.objects.filter(
            knowledge_base=self.kwargs['knowledge_base_pk'])
