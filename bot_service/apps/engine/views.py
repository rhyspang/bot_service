from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from bot_service.apps.engine.predictor import Predictor
from bot_service.apps.knowledge.models import KnowledgeItem
from bot_service.apps.user.serializers import UserSerializer
from bot_service.base_views import BaseViewSet
from bot_service.response.service_response import ServiceResponse as Response


predictor_dict = {}


class UserViewSet(BaseViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,
                       OrderingFilter)
    search_fields = ('username',)
    ordering_fields = ('id', 'username')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    user = User.objects.filter(username=request.user).first()
    user_serializer = UserSerializer(user, context={'request': request})
    return Response(user_serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    return Response()


class FormatTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return Response(response.data,)


@api_view(['GET'])
def train_model(request):
    global predictor_dict
    data = request.query_params
    knowledge_base_id = int(data['knowledge_base_id'])
    train_data = []
    for item in KnowledgeItem.objects.filter(knowledge_base_id=knowledge_base_id):
        train_data.append({
            'id': item.id,
            'question': item.question,
            'answers': [ans.content for ans in item.answers.all()],
            'similar_question': [qus.content for qus in item.similar_questions.all()]
        })
    predictor_dict[knowledge_base_id] = Predictor(train_data)
    return Response()


@api_view(['GET'])
def dialog(request):
    params = request.query_params
    predictor = predictor_dict[int(params['knowledge_base_id'])]
    return Response(predictor.predict(params['text']))
