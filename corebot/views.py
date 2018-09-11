import json

import telebot
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from telebot import types

from corebot.models import Place, User
from corebot.utils import distance
from telegrambot.bot import ChatBot
from telegrambot.cache_storage import CONFIRMATION, LOCATION, PHOTO, TITLE, \
    user_place

bot = getattr(ChatBot.get_instance(), 'bot')


def create_place_list_card(places):
    card = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton(text=place.title, callback_data=place.id) for
        place in places]
    card.add(*buttons)

    return card


def get_closest_places_for_user(user, location):
    lat = location.latitude
    lon = location.longitude
    places = [place for place in user.place_set.all() if
              distance((lat, lon), (place.latitude, place.longitude)) <= 500]

    return places


@bot.callback_query_handler(func=lambda x: True)  # Будет вызываться всегда
def choose_place_to_show_callback_handler(callback_query):
    message = callback_query.message
    data = callback_query.data
    place = Place.objects.get(id=data)
    bot.send_photo(
        chat_id=message.chat.id,
        photo=place.image.read(),
        caption=place.title
    )
    bot.send_location(
        chat_id=message.chat.id,
        latitude=place.latitude,
        longitude=place.longitude
    )


@bot.message_handler(commands=["help"])
def handle_app_place(message):
    help_message = '''
    Привет! Я могу помогать тебе помнить и всегда вернуться в места, которые тебе понравились. 
    Просто лови момент и дай знать, что запоминать.

    Ты можешь контролировать меня этими командами:
    
    <b>/start</b> - Скажу тебе, что я умею
    <b>/add</b>- Добавлю новое место, которое ты хочешь не забыть
    <b>/list</b> - Покажу тебе 10 последних мест, которые ты мне прислал
    <b>/reset</b> - Удалю все твои данные и забуду о тебе навсегда
    <b>/help</b> - Напомню о себе немного
    '''
    bot.send_message(message.chat.id, help_message, parse_mode="HTML")


@bot.message_handler(commands=["start"])
def handle_app_place(message):
    start_message = '''
    Ты можешь для начала использовть комманду <b>/start</b> чтобы начать.

    Если хочешь узнать больше обо мне, то используй команду <b>/help</b> 
    и я напомню о себе.
    Удачи!
    '''
    bot.send_message(message.chat.id, start_message, parse_mode="HTML")


@bot.message_handler(commands=["reset"])
def handle_app_place(message):
    try:
        User.objects.get(chat_id=message.chat.id).delete()
        bot.send_message(
            message.chat.id, text="Все, что я знал о тебе, я удалил. Пока!")
    except User.DoesNotExist:
        bot.send_message(message.chat.id, text="Я не знаю о тебе ничего.")


@bot.message_handler(commands=["add"])
def handle_app_place(message):
    bot.send_message(
        message.chat.id,
        text="Напиши название места, которое хочешь запомнить."
    )
    user_place.reset_user(message.chat.id)
    # Передаем обработку на следующий уровень.
    user_place.update_user_state(message.chat.id, TITLE)


@bot.message_handler(commands=["list"])
def handle_list_preview(message):
    try:
        user = User.objects.get(chat_id=message.chat.id)
    except User.DoesNotExist:
        bot.send_message(message.chat.id, text="Список мест пуст.")
    places = user.place_set.all()[:10]
    if places.count():
        card = create_place_list_card(places)
        bot.send_message(
            chat_id=message.chat.id,
            text="Вот что я нашел. Последние 10 мест, которые ты отметил.",
            reply_markup=card
        )
    else:
        bot.send_message(message.chat.id, text="Список мест пуст.")


@bot.message_handler(
    func=lambda message: user_place.get_user_state(message.chat.id) == TITLE)
def handler_title(message):
    if message.content_type == 'text':
        user_place.update_user_data(message.chat.id, message.text)
        bot.send_message(message.chat.id, text="Передай локацию места.")
        user_place.update_user_state(message.chat.id, LOCATION)
    else:
        bot.send_message(message.chat.id, text="Жду название.")


@bot.message_handler(
    content_types=['location', 'text'],
    func=lambda message: user_place.get_user_state(message.chat.id) == LOCATION
)
def handler_location(message):
    if message.content_type == 'location':
        loc = dict(
            latitude=message.location.latitude,
            longitude=message.location.longitude
        )
        user_place.update_user_data(message.chat.id, json.dumps(loc))
        bot.send_message(
            message.chat.id, text="Сделай фото места.")
        user_place.update_user_state(message.chat.id, PHOTO)
    else:
        bot.send_message(message.chat.id, text="Жду локацию.")


@bot.message_handler(
    content_types=['photo', 'text'],
    func=lambda message: user_place.get_user_state(message.chat.id) == PHOTO
)
def handler_photo(message):
    if message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        file_name = file_info.file_path.split('/')[-1]
        user_place.update_user_data(message.chat.id, file_name)
        downloaded_file = bot.download_file(file_info.file_path)
        user_place.update_user_data(message.chat.id, downloaded_file)
        title, _, _, _ = user_place.get_user_data(message.chat.id)
        bot.send_message(
            message.chat.id, text="Сохранить место? {}.".format(title))
        user_place.update_user_state(message.chat.id, CONFIRMATION)
    else:
        bot.send_message(message.chat.id, text="Жду фото.")


@bot.message_handler(
    func=lambda message: user_place.get_user_state(
        message.chat.id) == CONFIRMATION)
def handler_confirmation(message):
    if ('да' or 'сохранить') in message.text.lower():
        user, created = User.objects.get_or_create(
            first_name=message.from_user.first_name,
            last_name=message.from_user.first_name,
            chat_id=message.chat.id,
        )
        title, location, photo_name, photo = user_place.get_user_data(
            message.chat.id)
        place = Place.objects.create(
            user=user,
            title=title,
            latitude=location.get("latitude"),
            longitude=location.get("longitude")
        )
        place.image.save(photo_name, ContentFile(photo), save=False)
        place.save()
        bot.send_message(message.chat.id, text="Я сохранил это место.")
        user_place.reset_user(message.chat.id)
    elif 'нет' in message.text.lower():
        bot.send_message(message.chat.id, text="Нет проблем, все отменил.")
        user_place.reset_user(message.chat.id)
    else:
        bot.send_message(message.chat.id, text="Жду твое решение. Да или нет?")


@bot.message_handler(content_types=['location'])
def handle_plain_location(message):
    try:
        user = User.objects.get(chat_id=message.chat.id)
    except User.DoesNotExist:
        bot.send_message(message.chat.id, text="Список мест пуст.")
        return
    places = get_closest_places_for_user(user, message.location)
    if len(places):
        card = create_place_list_card(places)
        bot.send_message(
            chat_id=message.chat.id,
            text="Вот что я нашел поблизости.",
            reply_markup=card
        )
    else:
        bot.send_message(message.chat.id, text="Нет ничего подходящего рядом.")


@bot.message_handler()
def handle_message(message):
    bot.send_message(
        chat_id=message.chat.id,
        parse_mode="HTML",
        text="Похоже, что мне непонятно твое желение. "
             "Используй <b>/help</b> и я расскажу о себе."
    )


@csrf_exempt
@require_POST
def webhook(request):
    if request.META.get('CONTENT_TYPE') == 'application/json':
        update = telebot.types.Update.de_json(request.body.decode('utf-8'))
        bot.process_new_updates([update])
        return HttpResponse()
    else:
        response = HttpResponse('Permission required')
        response.status_code = 403
        return response
