import logging

from bot_service.apps.engine.predictor import Predictor
from bot_service.apps.knowledge.models import KnowledgeItem, KnowledgeBase

LOGGER = logging


class ModelManager(object):
    predictor_dict = {}
    shop_map = {}

    @staticmethod
    def train(knowledge_base_id):
        train_data = []
        knowledge_base = KnowledgeBase.objects.get(pk=knowledge_base_id)

        shop_id_list = knowledge_base.shop_id.split(',')
        shop_id_list = [item.strip() for item in shop_id_list]
        for item in shop_id_list:
            ModelManager.shop_map[item] = {
                'kb_id': knowledge_base_id,
                'name': knowledge_base.name
            }
        for item in KnowledgeItem.objects.filter(knowledge_base_id=knowledge_base_id):
            if not item.question:
                continue
            train_data.append({
                'id': item.id,
                'question': item.question,
                'answers': [ans.content for ans in item.answers.all()],
                'similar_question': [qus.content for qus in item.similar_questions.all() if qus.content]
            })
        ModelManager.predictor_dict[knowledge_base_id] = Predictor(train_data)
        LOGGER.debug('train knowledge base %s done', knowledge_base_id)

    @staticmethod
    def predict(shop_id, query_content):
        predictor = ModelManager.predictor_dict[ModelManager.shop_map[shop_id]['kb_id']]
        return predictor.predict(query_content, mode=3)
