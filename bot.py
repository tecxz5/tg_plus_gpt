import telebot
import gpt
from config import TOKEN

bot = telebot.TeleBot(TOKEN)

@bot.messsage_handler(commands=['start'])
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

@bot.message_handler(commands=['whitelist, debug, new_story, end_story'])
def null(message):
    bot.send_message(message.chat.id,
                     text="Команда-заглушка, пока не работает")

if __name__ == "__main__":
    print("Бот запускается....")
    bot.polling()