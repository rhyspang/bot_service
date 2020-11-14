import logging
from django.apps import AppConfig

LOGGER = logging


class KnowledgeConfig(AppConfig):
    name = 'bot_service.apps.knowledge'

    def ready(self):
        from bot_service.apps.engine.model_manager import ModelManager
        from bot_service.apps.knowledge.models import KnowledgeBase

        LOGGER.debug('train all knowledge base when app starting')
        for item in KnowledgeBase.objects.all():
            LOGGER.debug('train knowledge id: %s. name: %s. shopId: %s', item.id, item.name, item.shop_id)
            ModelManager.train(item.id)
