import telebot
from telebot import types as tgp
import config
import gpt
import database
import json

bot = telebot.TeleBot(config.TOKEN)
sql = database.SQL()
user_history = {}
sql.create_table()

ai_modes = [
    "Математика",
    "Кулинария",
    "Биология"
]

ai_desc = {
    "Математика": "Ты - дружелюбный помощник по математике. Давай подробный ответ с решением на русском языке",
    "Кулинария": "Ты - помощник по кулинарии. Давай подробный ответ с рецептом на русском языке",
    "Биология": "Ты - помощник по биологии. Давай подробный ответ с объяснением на русском языке",
}

level_desc = {
    "Новичок": "Объясни пожалуйста, я полностью глупый и ничего не понимаю",
    "Профисионал": "Объясни в чем проблема, но я уже хорошо помнимаю в этой теме"
}

def keyboard_gen(buttons: list) -> tgp.ReplyKeyboardMarkup:
    markup = tgp.ReplyKeyboardMarkup(one_time_keyboard=True)
    for button in buttons: markup.add(tgp.KeyboardButton(button))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_name = message.from_user.first_name
    bot.send_message(message.chat.id,
                     text=f"Привет, {user_name}! Я бот-помощник для решения разных задач!\n"
                          f"Ты можешь прислать условие задачи, а я постараюсь её решить.\n"
                          "Иногда (всегда) ответ будт получатся на английском так как токенайзер не хочет работать.\n"
                            "/solve_task - для вопросов, /help - для более подробной информации")

@bot.message_handler(commands=['help'])
def support(message):
    bot.send_message(message.from_user.id,
                     text=f"""Бот направлен на максимальную оптимизацию ответов, если у вас возникли какие-либо проблемы обращайтесь к разработчикам модели и лимиту токенов.
Рекомендуется скорее нажать /solve_task, так как зря писалось всё это?""")

@bot.message_handler(commands=['solve_task'])
def send_welcome(message: tgp.Message):
    bot.send_message(chat_id=message.chat.id, text="Выберите предмет:",
                     reply_markup=keyboard_gen(ai_modes))
    bot.register_next_step_handler(message, send_ai_answer)

@bot.message_handler(content_types=["text"], func=lambda message: False)
def send_ai_answer(message: tgp.Message):
    if not sql.has_user(message.chat.id):
        sql.create_user(message.chat.id)
    sql.set_ai(message.chat.id, message.text)
    bot.send_message(chat_id=message.chat.id, text="Выберете сложность задачи: ", reply_markup=keyboard_gen(["Новичок", "Профисионал"]))
    bot.register_next_step_handler(message, send_ai_level)

@bot.message_handler(content_types=["text"], func=lambda message: False)
def send_ai_level(message: tgp.Message):
    sql.set_level(message.chat.id, message.text)
    bot.send_message(chat_id=message.chat.id, text="Напишите задачу: ")
    bot.register_next_step_handler(message, send_ai_request_answer)

@bot.message_handler(content_types=["text"], func=lambda message: False)
def send_ai_request_answer(message: tgp.Message):
    ai_answer = bot.send_message(chat_id=message.chat.id, text="Нейросеть думает")
    json_parser = json.loads(sql.get_history(message.chat.id))
    story = [
        gpt.make_message("system", "Answer in Russian and do not translate the text into another language"),
        gpt.make_message("system", ai_desc[sql.get_mode(message.chat.id)]),
        gpt.make_message("assistant", "Решим задачу по шагам: "),
        gpt.make_message("assistant", json_parser["assistant"]),
        gpt.make_message(gpt.make_message("user", level_desc[sql.get_level(message.chat.id)])),
        gpt.make_message(gpt.make_message("user", json_parser["user"]+" "+message.text))
    ]
    rep = gpt.send_request(gpt.make_prompt(story))
    text = gpt.get_request(rep)
    next_story={
        "user": json_parser["user"]+" "+message.text,
        "assistant": json_parser["assistant"]+" "+message.text
    }
    _sql.set_gpt_history(message.chat.id, json.dumps(next_story))
    bot.edit_message_text(chat_id=message.chat.id, message_id=ai_answer.message_id, text=text)
    bot.send_message(chat_id=message.chat.id, reply_to_message_id=message.message_id, text="Сообщение доставлено",
                     reply_markup=keyboard_gen(["Продолжить", "Закончить"]))
    bot.register_next_step_handler(message, send_ai_question)

@bot.message_handler(content_types=["text"], func=lambda message: False)
def send_ai_question(message: tgp.Message):
    if message.text == "Закончить":
        bot.register_next_step_handler(message, send_welcome)
    elif message.text == "Продолжить":
        bot.register_next_step_handler(message, send_ai_request_answer)
    else:
        bot.register_next_step_handler(message, send_ai_request_answer)

if __name__ == "__main__":
    print("Бот запускается....")
    bot.polling()