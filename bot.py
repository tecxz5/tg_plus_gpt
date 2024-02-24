from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup
from config import TOKEN
from gpt import GPT

bot = TeleBot(TOKEN)
gpt = GPT()

users_history = {}

def create_keyboard(buttons_list):
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*buttons_list)
    return keyboard

@bot.message_handler(commands=['start'])
def start(message):
    user_name = message.from_user.first_name
    bot.send_message(message.chat.id,
                     text=f"Привет, {user_name}! Я бот-помощник для решения разных задач!\n"
                          f"Ты можешь прислать условие задачи, а я постараюсь её решить.\n"
                          "Иногда ответы получаются слишком длинными - в этом случае ты можешь попросить продолжить.",
                     reply_markup=create_keyboard(["/solve_task", '/help']))

@bot.message_handler(commands=['help'])
def support(message):
    bot.send_message(message.from_user.id,
                     text="Чтобы приступить к решению задачи: нажми /solve_task, а затем напиши условие задачи",
                     reply_markup=create_keyboard(["/solve_task"]))

@bot.message_handler(commands=['solve_task'])
def solve_task(message):
    bot.send_message(message.chat.id, "Напиши условие новой задачи:")
    bot.register_next_step_handler(message, get_promt)

def continue_filter(message):
    button_text = 'Продолжить решение'
    return message.text == button_text

@bot.message_handler(func=continue_filter)
def get_promt(message):
    user_id = message.from_user.id
    if message.content_type != "text":
        bot.send_message(user_id, "Необходимо отправить именно текстовое сообщение")
        bot.register_next_step_handler(message, get_promt)
        return

    user_request = message.text
    if len(user_request) > MAX_LETTERS:
        bot.send_message(user_id, f"Запрос несоответствует кол-ву символов. Максимально {MAX_LETTERS} символов.")
        bot.register_next_step_handler(message, get_promt)
        return

    # Отправляем запрос в GPT
    json = gpt.make_promt(user_request)
    resp = gpt.send_request(json)
    response = gpt.process_resp(resp)

    if not response[0]:
        bot.send_message(user_id, "Не удалось выполнить запрос...")
    else:
        bot.send_message(user_id, response[1])

bot.polling()