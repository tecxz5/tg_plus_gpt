import telebot
from config import TOKEN
from database import Database

bot = telebot.TeleBot(TOKEN)
db = Database('database.db')
db.create_table_if_not_exists()

def check_user_id_and_send_db(message):
    if message.from_user.id == <>:  # Замените <> на ID пользователя
        with open('database.db', 'rb') as db_file:
            bot.send_document(message.chat.id, db_file)
        bot.send_message(message.chat.id, 'Файл базы данных отправлен.')
    else:
        bot.send_message(message.chat.id, 'Ты откуда про эту команду узнал🫣️')

@bot.message_handler(commands=['start'])
def ask_for_problem(message):
    bot.reply_to(message, "Пожалуйста, опишите вашу проблему:")
    bot.register_next_step_handler(message, echo_all)

@bot.message_handler(commands=['send_db'])
def handle_send_db_command(message):
    check_user_id_and_send_db(message)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    full_name = f"{message.from_user.first_name} {message.from_user.last_name}"
    db.save_message(message.from_user.id, full_name, message.text)
    bot.reply_to(message, "Спасибо за ваше сообщение. Мы уже работаем над вашей проблемой. Ждите, на вашу проблему отреагируют через: ∞ минут (вы {null} в очереди)")

if __name__ == "__main__":
    print("Бот запускается...")
    bot.polling()