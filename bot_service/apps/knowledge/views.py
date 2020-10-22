# -*- coding: utf-8 -*-
import csv
import io
import logging

from django.contrib.auth.models import User
from django.http import HttpResponse
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

    @action(methods=['get'], detail=False, url_path='export_csv',
            url_name='export_csv')
    def export_csv(self, request, **kwargs):
        knowledge_set = self.get_queryset()
        # instance = self.get_object()
        response = HttpResponse(content_type='text/csv; charset=gbk')
        writer = csv.writer(response)
        writer.writerow(['知识点编号', '标准问', '相似问', '答案', '分类'])
        filename = 'knowledge.csv'
        for index, knowledge in enumerate(knowledge_set, 1):
            question_set = [knowledge.question]
            filename = f'{filename}_{knowledge.knowledge_base.id}'
            similar_questions = [item.content for item in knowledge.similar_questions.all()]
            answers = [item.content for item in knowledge.answers.all()]
            max_len = max(len(question_set), len(similar_questions), len(answers))
            for row in range(max_len):
                question = question_set[row] if row < len(question_set) else ''
                similar_question = similar_questions[row] if row < len(similar_questions) else ''
                answer = answers[row] if row < len(answers) else ''
                writer.writerow([index, question, similar_question, answer, knowledge.scope])
        logging.debug('filename: %s', filename)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return

    @action(methods=['post'], detail=False, url_path='import_csv',
            url_name='import_csv')
    def import_csv(self, request, **kwargs):
        file = request.FILES.get("file")
        user = User.objects.filter(username=request.user).first()
        knowledge_base = KnowledgeBase.objects.get(pk=kwargs['knowledge_base_pk'])
        csv_data = {}
        try:
            decoded_file = file.read().decode('gbk')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            for item in reader:
                knowledge_index = item['知识点编号']
                if knowledge_index not in csv_data:
                    csv_data[knowledge_index] = {
                        'answers': [],
                        'similar_questions': [],
                        'question': item['标准问'],
                        'scope': item.get('分类', 0),
                        'created_by': user,
                        'knowledge_base': knowledge_base
                    }
                    if item['相似问']:
                        csv_data[knowledge_index]['similar_questions'].append({
                            'content': item['相似问']
                        })
                    if item['答案']:
                        csv_data[knowledge_index]['answers'].append({
                            'content': item['答案']
                        })
        except Exception as e:
            logging.exception(e)
            return Response(code=10001, message='文件格式错误，缺少' + str(e) + '字段')

        for values in csv_data.values():
            serializer = self.serializer_class()
            serializer.create(values)
        return Response()
