import telebot
import logging
from functools import wraps
from gpt import PyYandexGpt
from config import TOKEN, WHITELISTED_USERS, GPT_TOKEN, GPT_URL

bot = telebot.TeleBot(TOKEN)
gpt_client = PyYandexGpt(GPT_TOKEN, GPT_URL, 'yandexgpt-lite')
logging.basicConfig(level=logging.DEBUG)

def is_user_whitelisted(chat_id):
    return chat_id in WHITELISTED_USERS

def private_access():
    def deco_restrict(f):
        @wraps(f)
        def f_restrict(message, *args, **kwargs):
            user_id = message.from_user.id
            if is_user_whitelisted(user_id):
                return f(message, *args, **kwargs)
            else:
                bot.reply_to(message, text='У вас нету доступа к YaGPT')
        return f_restrict
    return deco_restrict

@bot.message_handler(commands=['start'])
def start(message):
    user_name = message.from_user.first_name
    bot.send_message(message.chat.id,
                     text=f"""
Привет, {user_name}! Я бот-сценарист для придумывания разных историй.
От тебя требуется фантазия и выбор жанров, персонажей и сеттингов(где происходят действие).
Напиши /new_story и давай же начнем!""")

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

@bot.message_handler(commands=['debug'])
def debug(message):
    bot.send_message(message.chat.id,
                     text="Планируется высылание логов")


@bot.message_handler(commands=['new_story'])
@private_access()
def new_story(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Пожалуйста, введите текст для истории:")

@bot.message_handler(commands=['end_story'])
def null(message):
    bot.send_message(message.chat.id,
                     text="Команда-заглушка, пока не работает")

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text_message(message):
    chat_id = message.chat.id
    text = message.text # Получаем текст сообщения от пользователя
    prompt = text # Используем текст сообщения как prompt
    response = gpt_client.create_request(chat_id, prompt)
    if response.status_code == 200:
        try:
            result_text = response_json['result']['alternatives'][0]['message']['text']
            bot.send_message(chat_id, result_text)
        except KeyError:
            logging.error('Ответ от API GPT не содержит ключа "result"')
            bot.send_message(chat_id, "Извините, не удалось сгенерировать историю.")
    else:
        logging.error(f'Ошибка API GPT: {response.status_code}')
        bot.send_message(chat_id, "Извините, произошла ошибка при обращении к API GPT.")

if __name__ == "__main__":
    print("Бот запускается...")
    bot.polling()