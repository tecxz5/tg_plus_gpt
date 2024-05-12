import telebot
import logging
import functools
from telebot import types
from yandex_gpt import PyYandexGpt
from database_YaGPT import Tokens
from database_history import History
from database_SpeechKit import SpeechKit
from speechkit import text_to_speech, speech_to_text
from config import TOKEN, WHITELISTED_USERS, IAM_TOKEN, FOLDER_ID

bot = telebot.TeleBot(TOKEN)
dbt = Tokens("tokens.db")
dbh = History("history.db")
dbS = SpeechKit()
logging.basicConfig(level=logging.DEBUG)
dbt.create_tables()
dbS.create_database()

def is_user_whitelisted(chat_id): # используется в /whitelist и декораторе
    return chat_id in WHITELISTED_USERS

def whitelist_check(func):
    @functools.wraps(func)
    def wrapper(message):
        chat_id = message.chat.id
        if chat_id not in WHITELISTED_USERS:
            bot.send_message(chat_id, "У тебя нету доступа к этой команде/функционалу, так как ты не в вайтлисте (/whitelist)")
            return
        return func(message)
    return wrapper

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_name = message.from_user.first_name
    dbt.create_user_profile(chat_id)
    dbS.add_user(chat_id)
    bot.send_message(chat_id,
                     text=f"""
Привет, {user_name}! Я скорее всего твой собеседник или переработка писателя историй, но не об этом, ты мне можешь отправлять и текстовыые сообщения и голосовые, я на те и те буду отвечать, кружки не пробуй, в любом случае, я твоего слова жду😉""")

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id,
                      text="""
Бот работает на базе YaGPT(ЯЖПТ) и SpeechKit
Документация бота здесь - https://hoprik.ru/u/11bc18
Проверить можете ли вы воспользоваться ботом здеся: /whitelist""")

@bot.message_handler(commands=['whitelist'])
def whitelist(message):
    chat_id = message.chat.id
    if is_user_whitelisted(chat_id):
        bot.send_message(chat_id, 'У вас есть доступ к YaGPT')
    else:
        bot.send_message(chat_id, 'У вас нету доступа к YaGPT')

@bot.message_handler(commands=['stt'])
def stt(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, f"Команда-пустышка")

@bot.message_handler(commands=['tts'])
@whitelist_check
def tts(message):
    chat_id = message.chat.id
    current_characters = dbS.get_token_count(chat_id)

    # Проверка, достаточно ли символов для обработки запроса
    if current_characters < 10:
        bot.send_message(chat_id, "Недостаточно символов. Озвучить текст невозможно")
        return
    bot.send_message(chat_id, "Пожалуйста, введите текст для синтеза речи:")
    bot.register_next_step_handler(message, handle_tts)

@bot.message_handler(commands=['debug'])
def debug(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, f"Команда-пустышка")

@bot.message_handler(commands=['clear'])
def clear(message):
    chat_id = message.chat.id
    dbh.clear_history(chat_id)
    bot.send_message(chat_id, "История отчищена")


@bot.message_handler(commands=['profile'])
def tokens_handler(message):
    chat_id = message.chat.id
    user_name = message.from_user.first_name
    tokens = dbt.get_tokens(chat_id)
    symbols = dbS.get_token_count(chat_id)
    blocks = None
    bot.send_message(chat_id, f"""Информация по пользователю {user_name}

Кол-во оставшихся токенов: {tokens}
Кол-ва оставшихся символов: {symbols}
Кол-во оставшихся блоков: {blocks}""")

@bot.message_handler(content_types=['text'])
@whitelist_check
def text_reply(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Я тебе буду отвечать только одной заготовленной фразой😊')


@bot.message_handler(content_types=['voice'])
@whitelist_check
def voice_reply(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Пока ответить на голосовое сообщение голосовым я не могу😥")

def handle_tts(message):
    chat_id = message.chat.id
    text = message.text
    current_characters = dbS.get_token_count(chat_id)
    if current_characters - len(text) < 0: # проверка на то, что пользователь не уйдет в минус
        bot.send_message(chat_id, "Ты перешел лимит своих токенов, сделай текст покороче")
        return
    if len(text) >= 100: # проверка на кол-во символов
        bot.send_message(chat_id, "Ты написал текст длинне 100 символов, сделай текст покороче")
        return
    current_characters = dbS.get_token_count(chat_id)
    success, audio_file_path = text_to_speech(text, str(chat_id))
    if success:
        dbS.update_token_count(chat_id, current_characters - len(text))
        bot.send_audio(chat_id, open(audio_file_path, 'rb'))
    else:
        bot.send_message(chat_id, "Ошибка при синтезе речи.")

if __name__ == "__main__":
    print("Бот запускается...")
    logging.info("Бот запускается...")
    bot.polling()