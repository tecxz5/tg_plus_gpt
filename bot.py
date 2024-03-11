from telebot import TeleBot, types
from config import TOKEN, MAX_TOKENS
from gpt import GPT, themes_and_levels
from database import create_database, add_user_data, update_user_data, get_user_data, save_subject_and_level

create_database()

bot = TeleBot(TOKEN)
gpt = GPT()
users_history = {}

def create_keyboard(buttons_list):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*buttons_list)
    return keyboard

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
def solve_task(message):
    user_id = message.chat.id
    task = message.text
    profile = get_user_data(user_id, 'bot_database.db')
    if not profile:
        bot.send_message(user_id, "Пожалуйста, выберите профиль с помощью команды /select_profile.")
        return
    add_user_data(user_id, profile[1], profile[2], task, "")
    gpt_response = "Ответ от GPT"
    update_user_data(user_id, gpt_response=gpt_response)

@bot.message_handler(commands=['select_profile'])
def select_profile(message):
    user_id = message.chat.id
    markup = types.InlineKeyboardMarkup()
    for subject in themes_and_levels.keys():
        markup.add(types.InlineKeyboardButton(subject, callback_data=subject))
    bot.send_message(user_id, "Выберите предмет:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_subject_selection(call):
    selected_subject = call.data
    user_id = call.message.chat.id
    # Проверяем, был ли уже выбран уровень сложности для данного пользователя
    user_subject_level = get_user_data(user_id, 'bot_database.db')
    if user_subject_level:
        # Если уровень сложности уже выбран, пропускаем предложение выбора
        bot.send_message(user_id, f"Вы уже выбрали: {user_subject_level}")
        return
    # Если уровень сложности не выбран, предлагаем выбрать уровень
    levels = themes_and_levels.get(selected_subject, {})
    markup = types.InlineKeyboardMarkup()
    for level in levels.keys():
        markup.add(types.InlineKeyboardButton(level, callback_data=f"{selected_subject}_{level}"))
    bot.send_message(user_id, f"Выбран предмет: {selected_subject}. Теперь выберите уровень:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_subject_selection(call):
    selected_subject_level = call.data
    user_id = call.message.chat.id
    # Просто выводим выбранный предмет и уровень
    bot.send_message(user_id, f"Вы выбрали: {selected_subject_level}")

@bot.message_handler(commands=['continue'])
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

@bot.message_handler(commands=['debug'])
def send_debug_info(message):
    user_id = message.from_user.id
    try:
        with open('gpt_errors.log', 'rb') as file:
            bot.send_document(user_id, file)
    except FileNotFoundError:
        bot.send_message(user_id, "Файл логов не найден.")

bot.polling()