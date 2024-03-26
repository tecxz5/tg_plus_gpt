import telebot
import logging
from functools import wraps
from gpt import PyYandexGpt
from database import Database
from config import TOKEN, WHITELISTED_USERS, GPT_TOKEN, GPT_URL

bot = telebot.TeleBot(TOKEN)
db = Database("tokens.db")
gpt_client = PyYandexGpt(GPT_TOKEN, GPT_URL, 'yandexgpt-lite') # не самое верное стратегическое решение но всё же
logging.basicConfig(level=logging.DEBUG)
user_sessions = {}
db.create_tables()

def is_user_whitelisted(chat_id): # используется в /whitelist и декораторе
    return chat_id in WHITELISTED_USERS

def private_access(): # декоратор работающий на одну команду, на других ноет что не работает, да и не надо
    def deco_restrict(f):
        @wraps(f)
        def f_restrict(message, *args, **kwargs):
            user_id = message.from_user.id
            if is_user_whitelisted(user_id):
                return f(message, *args, **kwargs)
            else:
                bot.reply_to(message, text='У вас нету доступа к этой команде!')
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

@bot.message_handler(commands=['debug'])  # примерно то же самое что было в первом дз, только без заморочек
def debug(message):
    chat_id = message.chat.id
    try:
        with open('bot_logs.log', 'rb') as log_file:
            bot.send_document(chat_id, log_file)
        bot.send_message(chat_id, "Файл с логами отправлен.")
    except Exception as e:
        bot.send_message(chat_id, f"Ошибка при отправке файла с логами: {e}")

@bot.message_handler(commands=['new_story'])
@private_access() # это же тот самый декоратор чтоооооо
def new_story(message):
    chat_id = message.chat.id
    user_sessions[chat_id] = True
    bot.send_message(chat_id, "Пожалуйста, введите текст для истории:")

@bot.message_handler(commands=['end_story'])
def end_history(message):
    chat_id = message.chat.id
    if chat_id not in user_sessions or not user_sessions[chat_id]:
        bot.send_message(chat_id, "Вы не начали новую историю. Напишите /new_story для начала.") # горжусь этой функцией
        return
    user_sessions[chat_id] = False
    bot.send_message(chat_id, "История закончена")

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text_message(message):
    chat_id = message.chat.id
    if chat_id not in user_sessions or not user_sessions[chat_id]:
        bot.send_message(chat_id, "Вы не начали новую историю. Напишите /new_story для начала.") # горжусь этой функцией
        return
    else:
        text = message.text # Получаем текст сообщения от пользователя
        prompt = text # Используем текст сообщения как prompt
        tokens_count = gpt_client.count_tokens(text)
        print(f"Количество токенов: {tokens_count}")
        response = gpt_client.create_request(chat_id, prompt)
        if response.status_code == 200:
            try:
                response_json = response.json()
                result_text = response_json['result']['alternatives'][0]['message']['text']
                logging.info(result_text)
                bot.send_message(chat_id, result_text)
            except KeyError:
                logging.error('Ответ от API GPT не содержит ключа "result"')
                bot.send_message(chat_id, "Извините, не удалось сгенерировать историю.")
        else:
            logging.error(f'Ошибка API GPT: {response.status_code}')
            bot.send_message(chat_id, f"""
Извините, произошла ошибка при обращении к API GPT.
Ошибка: {response.status_code}
||Если ошибка 429 - нейросеть просит не так часто писать промпты||""",
                         parse_mode='MarkdownV2')

if __name__ == "__main__":
    print("Бот запускается...")
    logging.info("Бот запускается...")
    bot.polling()