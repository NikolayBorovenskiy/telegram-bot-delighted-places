import telebot

from django.conf import settings


class ChatBot:
    _instance = None

    def __init__(self, host_name, token):
        self.host_name = host_name
        self.token = token
        self.bot = telebot.TeleBot(self.token)
        self.bot.remove_webhook()
        self.bot.set_webhook(url=self.host_name + '/weebhook/' + self.token)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls(settings.WEBHOOK_HOST_NAME,
                                settings.TELEGRAM_TOKEN)
        return cls._instance
