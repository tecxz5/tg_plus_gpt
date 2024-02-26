from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup
from config import TOKEN, MAX_TOKENS
from gpt import GPT

bot = TeleBot(TOKEN)
gpt = GPT()
users_history = {}

def create_keyboard(buttons_list):
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*buttons_list)
    return keyboard

@bot.message_handler(commands=['start']) # /start
def start(message):
    user_name = message.from_user.first_name
    bot.send_message(message.chat.id,
                     text=f"Привет, {user_name}! Я бот-помощник для решения разных задач!\n"
                          f"Ты можешь прислать условие задачи, а я постараюсь её решить.\n"
                          "Иногда (всегда) ответ будт получатся на английском так как токенайзер не хочет работать.\n"
                            "/solve_task - для вопросов, /help - для более подробной информации",
                     reply_markup=create_keyboard(["/solve_task", '/help']))

@bot.message_handler(commands=['help']) #/help
def support(message):
    bot.send_message(message.from_user.id,
                     text=f"""Бот направлен на максимальную оптимизацию ответов, если у вас возникли какие-либо проблемы обращайтесь к разработчикам модели и лимиту токенов.
Рекомендуется скорее нажать /solve_task, так как зря писалось всё это?""",
                     reply_markup=create_keyboard(["/solve_task"]))

@bot.message_handler(commands=['solve_task']) # /solve_task
def solve_task(message):
    bot.send_message(message.chat.id, "Напиши условие новой задачи:")
    bot.register_next_step_handler(message, get_promt)

@bot.message_handler(commands=['continue']) # /continue
def continue_solve_task(message):
    user_id = message.from_user.id
    if user_id not in users_history or not users_history[user_id]['user_request']:
        bot.send_message(user_id, "Нет предыдущего запроса для продолжения.")
        return

    user_request = users_history[user_id]['user_request']
    json = gpt.make_promt(user_request)
    resp = gpt.send_request(json)
    response = gpt.process_resp(resp)

    if not response[0]:
        bot.send_message(user_id, "Не удалось выполнить запрос...")
    else:
        bot.send_message(user_id, response[1])
        gpt.clear_history()

@bot.message_handler(commands=['debug']) # /debug
def send_debug_info(message):
    user_id = message.from_user.id
    try:
        with open('gpt_errors.log', 'rb') as file:
            bot.send_document(user_id, file)
    except FileNotFoundError:
        bot.send_message(user_id, "Файл логов не найден.")

bot.message_handler(func=lambda message: True) # функция гет промпт для отправки в gpt
def get_promt(message):
    user_id = message.from_user.id
    user_request = message.text
    # Создаем новый экземпляр GPT для каждого нового запроса
    gpt_instance = GPT()
    json = gpt_instance.make_promt(user_request)
    resp = gpt_instance.send_request(json)
    response = gpt_instance.process_resp(resp)

    if not response[0]:
        bot.send_message(user_id, "Не удалось выполнить запрос...")
    else:
        # Добавляем ответ в историю пользователя
        if user_id not in users_history:
            users_history[user_id] = {'user_request': user_request, 'response': response[1]}
        else:
            users_history[user_id]['user_request'] += "\n" + user_request
            users_history[user_id]['response'] += "\n" + response[1]
        bot.send_message(user_id, response[1])

bot.polling()