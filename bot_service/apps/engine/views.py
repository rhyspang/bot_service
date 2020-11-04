import json
import logging
import time
import random

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


LOGGER = logging
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

    shop_id_list = knowledge_base.shop_id.split(',')
    shop_id_list = [item.strip() for item in shop_id_list]
    for item in shop_id_list:
        shop_map[item] = {
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
    LOGGER.debug("raw query: %s", json.dumps(raw_query))
    to_user_id = raw_query['message']['from']['uid']
    shop_id = raw_query['message']['to']['uid']
    value2 = raw_query['message']['titan_msg_id'].split('#')[1]
    from_shop_id = f'cs_{shop_id}_{value2}'
    query_content = raw_query['message']['content']
    LOGGER.debug('query text: %s', query_content)

    if shop_id not in shop_map:
        LOGGER.debug('shop id not in shop map: %s', shop_id)
        return Response({
            'status': False,
            'code': 1002,
            'to_user_id': to_user_id,
            'from_shop_id': from_shop_id,
            'content': '',
            'shop_id': shop_id,
            'shop_name': '',
            'msg': f'no shop config: {shop_id}'
        })

    try:
        predictor = predictor_dict[shop_map[shop_id]['kb_id']]
        content, status = predictor.predict(query_content, mode=3)
        response_text = content[0]['answer'] if status else ''

        if status:
            LOGGER.debug('response text: %s', response_text)
            code = 1000
            score = content[0]['score']
            msg = 'ok'
        else:
            code = 1001
            score = 0
            msg = 'no knowledge match'
        response_data = {
            'status': status,
            'code': code,
            'to_user_id': to_user_id,
            'from_shop_id': from_shop_id,
            'content': response_text,
            'shop_id': shop_id,
            'shop_name': shop_map[shop_id]['name'],
            'msg': msg,
            'score': score
        }
        LOGGER.debug("response: %s", json.dumps(response_data))
        random_time = random.randint(1000, 4000)
        LOGGER.debug('deny response time: %s', random_time)
        time.sleep(random_time / 1000.)
        return Response(response_data)
    except Exception as e:
        LOGGER.exception(e)
        return Response({
            'status': False,
            'code': 1100,
            'to_user_id': to_user_id,
            'from_shop_id': from_shop_id,
            'content': '',
            'shop_id': shop_id,
            'shop_name': '',
            'msg': 'unknown error'
        })
