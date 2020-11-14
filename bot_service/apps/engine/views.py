import json
import logging
import random
import time

from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from bot_service.apps.engine.model_manager import ModelManager
from bot_service.apps.user.serializers import UserSerializer
from bot_service.base_views import BaseViewSet
from bot_service.response.service_response import ServiceResponse as Response

LOGGER = logging
DLOGGER = logging.getLogger('record_logger')


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
    data = request.query_params
    knowledge_base_id = int(data['knowledge_base_id'])
    ModelManager.train(knowledge_base_id)
    return Response()


@api_view(['GET'])
def dialog(request):
    params = request.query_params
    predictor = ModelManager.predictor_dict[int(params['knowledge_base_id'])]
    return Response(predictor.predict(params['text']))


def log_data(query_data, answer_data):
    all_data = {
        'request': query_data,
        'response': answer_data
    }
    DLOGGER.debug(json.dumps(all_data, ensure_ascii=False))


@api_view(['POST'])
@permission_classes([])
def dialog_store(request):
    data = request.data
    raw_query = json.loads(data['query'])
    LOGGER.debug("raw query: %s", json.dumps(raw_query, ensure_ascii=False))
    to_user_id = raw_query['message']['from']['uid']
    shop_id = raw_query['message']['to']['uid']
    value2 = raw_query['message']['titan_msg_id'].split('#')[1]
    from_shop_id = f'cs_{shop_id}_{value2}'
    query_content = raw_query['message']['content']
    LOGGER.debug('query text: %s', query_content)

    if shop_id not in ModelManager.shop_map:
        LOGGER.debug('shop id not in shop map: %s', shop_id)
        res = {
            'status': False,
            'code': 1002,
            'to_user_id': to_user_id,
            'from_shop_id': from_shop_id,
            'content': '',
            'shop_id': shop_id,
            'shop_name': '',
            'msg': f'no shop config: {shop_id}'
        }
        log_data(raw_query, res)
        return Response(res)

    try:
        content, status = ModelManager.predict(shop_id, query_content)
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
            'shop_name': ModelManager.shop_map[shop_id]['name'],
            'msg': msg,
            'score': score
        }
        LOGGER.debug("response: %s", json.dumps(response_data, ensure_ascii=False))
        random_time = 0
        if status:
            random_time = random.randint(1000, 4000)
            LOGGER.debug('deny response time: %s', random_time)
            time.sleep(random_time / 1000.)
        response_data['delay_response'] = random_time
        log_data(raw_query, response_data)
        return Response(response_data)
    except Exception as e:
        LOGGER.exception(e)
        res = {
            'status': False,
            'code': 1100,
            'to_user_id': to_user_id,
            'from_shop_id': from_shop_id,
            'content': '',
            'shop_id': shop_id,
            'shop_name': '',
            'msg': 'unknown error',
            'e': str(e)
        }
        log_data(raw_query, res)
        return Response(res)
