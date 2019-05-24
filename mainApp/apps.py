from django.apps import AppConfig
import os


class MainappConfig(AppConfig):
    name = 'mainApp'
    def ready(self):
        os.makedirs('./music', exist_ok=True)
        os.makedirs('./log', exist_ok=True)
        os.makedirs('./life', exist_ok=True)
