import telebot
import logging
from telebot import types
from yandex_gpt import PyYandexGpt
from database_YaGPT import Tokens
from database_history import History
from database_SpeechKit import SpeechKit
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
Все запросы генерируются через YaGPT, и из-за этого не все могут воспользоваться генерацией текста, так что не расстраивайтесь, если вы не из этих людей
Так же можно проверить есть ли вы в этом списке с помощью команды /whitelist""")

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
def tts(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, f"Команда-пустышка")

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
def text_reply(message):
    bot.send_message(message.chat.id, 'Я тебе буду отвечать только одной заготовленной фразой😊')

@bot.message_handler(content_types=['voice'])
def voice_reply(message):
    bot.send_message(message.chat.id, "Пока ответить на голосовое сообщение голосовым я не могу😥")

if __name__ == "__main__":
    print("Бот запускается...")
    logging.info("Бот запускается...")
    bot.polling()