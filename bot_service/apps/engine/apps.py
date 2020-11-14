import logging

from django.apps import AppConfig

LOGGER = logging


class EngineConfig(AppConfig):
    name = 'bot_service.apps.engine'
