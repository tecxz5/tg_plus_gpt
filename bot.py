import math
import telebot
import logging
import functools
from auto_token import update_config_file
from yandex_gpt import PyYandexGpt
from database_YaGPT import Tokens
from database_history import History
from config import TOKEN, WHITELISTED_USERS

bot = telebot.TeleBot(TOKEN)
dbt = Tokens("tokens.db")
dbh = History("history.db")
gpt = PyYandexGpt()
logging.basicConfig(level=logging.DEBUG)
dbt.create_tables()

system_prompt = "Ты - собеседник женского пола, общайся с пользователем"

def is_user_whitelisted(chat_id): # используется в /whitelist и декораторе
    return chat_id in WHITELISTED_USERS

def whitelist_check(func):
    """Поздравьте нормально работающий декоратор"""
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
    dbt.create_user_profile(chat_id)
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

@bot.message_handler(commands=['profile'])
def tokens_handler(message):
    chat_id = message.chat.id
    user_name = message.from_user.first_name
    tokens = dbt.get_tokens(chat_id)
    symbols = dbS.get_token_count(chat_id)
    blocks = dbS.get_blocks_vount(chat_id)
    bot.send_message(chat_id, f"""Информация по пользователю {user_name}

Кол-во оставшихся токенов: {tokens}
""")

@bot.message_handler(content_types=['text'])
@whitelist_check
def text_reply(message):
    chat_id = message.chat.id
    current_tokens = dbt.get_tokens(chat_id)
    if current_tokens == 0:
        bot.send_message(chat_id,
                         "Ваши токены закончились, функция общения с нейросетью невозможна")
    else:
        text = message.text  # Получаем текст сообщения от пользователя
        user_history = dbh.get_history(message.chat.id)
        history_text = "\n".join([f"{row[0]}: {row[1]} ({row[2]})" for row in user_history])
        logging.info(f"История общения: {history_text}")
        final_text = f"{text}, История чата: {history_text}"
        system_text = system_prompt
        prompt = [{"role": "system",
                   "text": system_text},
                  {"role": "user",
                   "text": final_text}]  # Используем текст сообщения как prompt
        response = gpt.create_request(chat_id, prompt)
        if response.status_code == 200:
            try:
                response_json = response.json()
                result_text = response_json['result']['alternatives'][0]['message']['text']
                logging.info(response_json)
                count = gpt.count_tokens(final_text)
                dbt.deduct_tokens(chat_id, count)
                bot.send_message(chat_id, result_text)
                dbh.save_message(chat_id, 'user', text)
                dbh.save_message(chat_id, 'assistant', result_text)
                logging.info(f"История ответа от пользователя {chat_id} сохранена")
                return
            except KeyError:
                logging.error('Ответ от API GPT не содержит ключа "result"')
                bot.send_message(chat_id, "Извините, не удалось сгенерировать историю.")
        else:
            logging.error(f'Ошибка API GPT: {response.status_code}')
            bot.send_message(chat_id, f"""
        Извините, произошла ошибка при обращении к API GPT.
        Ошибка: {response.status_code}
        Если ошибка 429 - нейросеть просит не так часто писать промпты либо же она нагружена""")
            return

if __name__ == "__main__":
    print("Бот запускается...")
    logging.info("Бот запускается...")
    bot.polling()