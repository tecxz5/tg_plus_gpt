import telebot
import logging
import functools
from database_history import History
from config import TOKEN, WHITELISTED_USERS

bot = telebot.TeleBot(TOKEN)
dbh = History("history.db")
logging.basicConfig(level=logging.DEBUG)

def is_user_whitelisted(chat_id): # используется в /whitelist и декораторе
    return chat_id in WHITELISTED_USERS

def whitelist_check(func):
    """Поздравьте, нормально работающий декоратор"""
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
    dbh.create_table(chat_id)
    bot.send_message(chat_id,
                     text=f"""
Привет, {user_name}! Я скорее всего твой собеседник или переработка писателя историй, но не об этом, ты мне можешь отправлять и текстовыые сообщения и голосовые, я на те и те буду отвечать, кружки не пробуй, в любом случае, я твоего слова жду😉""")

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id,
                      text="""
Бот работает на базе Gemini
Проверить можете ли вы воспользоваться ботом здесь: /whitelist""")

@bot.message_handler(commands=['whitelist'])
def whitelist(message):
    chat_id = message.chat.id
    if is_user_whitelisted(chat_id):
        bot.send_message(chat_id, 'У вас есть доступ к YaGPT')
    else:
        bot.send_message(chat_id, 'У вас нету доступа к YaGPT')

@bot.message_handler(commands=['clear'])
def clear(message):
    chat_id = message.chat.id
    dbh.clear_history(chat_id)
    bot.send_message(chat_id, "История отчищена")