import telebot
import logging
from gpt import PyYandexGpt
from config import TOKEN, WHITELISTED_USERS, GPT_TOKEN, GPT_URL

bot = telebot.TeleBot(TOKEN)
gpt_client = PyYandexGpt(GPT_TOKEN, GPT_URL, 'yandexgpt-lite')
logging.basicConfig(level=logging.DEBUG)

def is_user_whitelisted(chat_id):
    return chat_id in WHITELISTED_USERS

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
def null(message):
    bot.send_message(message.chat.id,
                     text="Команда-заглушка, пока не работает")


@bot.message_handler(commands=['new_story'])
def new_story(message):
    chat_id = message.chat.id
    if is_user_whitelisted(chat_id):
        prompt = "Напишите историю о..."
        response = gpt_client.create_request(chat_id, prompt)
        logging.debug(f"Получен ответ: {response.text}")
        if response:
            bot.send_message(chat_id, response["result"])
        else:
            bot.send_message(chat_id, "Извините, не удалось сгенерировать историю.")
    else:
        bot.send_message(chat_id, 'У вас нету доступа к YaGPT')

@bot.message_handler(commands=['end_story'])
def null(message):
    bot.send_message(message.chat.id,
                     text="Команда-заглушка, пока не работает")

if __name__ == "__main__":
    print("Бот запускается....")
    bot.polling()