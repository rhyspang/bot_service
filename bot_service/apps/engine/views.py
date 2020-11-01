import base64
import json
import logging

from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from bot_service.apps.engine.predictor import Predictor
from bot_service.apps.knowledge.models import KnowledgeItem, KnowledgeBase
from bot_service.apps.user.serializers import UserSerializer
from bot_service.base_views import BaseViewSet
from bot_service.response.service_response import ServiceResponse as Response


predictor_dict = {}
shop_map = {}


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
    global shop_map
    data = request.query_params
    knowledge_base_id = int(data['knowledge_base_id'])
    train_data = []
    knowledge_base = KnowledgeBase.objects.get(pk=knowledge_base_id)
    shop_map[knowledge_base.shop_id] = {
        'kb_id': knowledge_base_id,
        'name': knowledge_base.name
    }
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


@api_view(['POST'])
@permission_classes([])
def dialog_store(request):
    global predictor_dict
    global shop_map
    data = request.data
    raw_query = json.loads(data['query'])
    logging.info(raw_query)
    to_user_id = raw_query['message']['from']['uid']
    shop_id = raw_query['message']['to']['uid']
    value2 = raw_query['message']['titan_msg_id'].split('#')[1]
    from_shop_id = f'cs_{shop_id}_{value2}'

    try:
        content = predictor_dict[shop_map[shop_id]['kb_id']].predict(raw_query['message']['content'])
        status = bool(content)
        response_text = content[0]['answer'];
        return Response({
            'status': status,
            'to_user_id': to_user_id,
            'from_shop_id': from_shop_id,
            'content': response_text,
            'shop_id': shop_id,
            'shop_name': shop_map[shop_id]['name']
        })
    except Exception as e:
        logging.error(e)
        return Response({
            'status': False,
            'to_user_id': to_user_id,
            'from_shop_id': from_shop_id,
            'content': '',
            'shop_id': shop_id,
            'shop_name': '',
        })
