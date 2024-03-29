import telebot
import logging
from telebot import types
from functools import wraps
from gpt import PyYandexGpt
from database_token import Tokens
from database_history import History
from config import TOKEN, WHITELISTED_USERS, GPT_TOKEN, GPT_URL

bot = telebot.TeleBot(TOKEN)
dbt = Tokens("tokens.db")
dbh = History("history.db")
gpt_client = PyYandexGpt(GPT_TOKEN, GPT_URL, 'yandexgpt-lite') # не самое верное стратегическое решение но всё же
logging.basicConfig(level=logging.DEBUG)
user_sessions = {}
current_state = {}
dbt.create_tables()
genre = ""
main_person = ""
setting = ""
final_choice = ""

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

# Создание клавиатуры для выбора жанра
def create_genre_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2)
    markup.add(types.KeyboardButton('Фентези'), types.KeyboardButton('Научная фантастика'), types.KeyboardButton('Детектив'), types.KeyboardButton('Боевик'))
    return markup

# Создание клавиатуры для выбора персонажей
def create_character_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2)
    markup.add(types.KeyboardButton('Анна'), types.KeyboardButton('Алексей'), types.KeyboardButton('Мария'), types.KeyboardButton('Иван'))
    return markup

# Создание клавиатуры для выбора сеттинга
def create_setting_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2)
    markup.add(types.KeyboardButton('Постапокалипсис'), types.KeyboardButton('Пустыня'), types.KeyboardButton('Город'))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_name = message.from_user.first_name
    dbt.create_user_profiles(chat_id)
    bot.send_message(chat_id,
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
        with open('logs.log', 'rb') as log_file:
            bot.send_document(chat_id, log_file)
        bot.send_message(chat_id, "Файл с логами отправлен.")
    except Exception as e:
        bot.send_message(chat_id, f"Ошибка при отправке файла с логами: {e}")

@bot.message_handler(commands=['used_tokens'])
def used_tokens_handler(message):
    chat_id = message.chat.id
    tokens_used = dbt.get_tokens_used(chat_id)
    bot.send_message(chat_id, f"Вы потратили {tokens_used} токенов.")

@bot.message_handler(commands=['sessions'])
def sessions(message):
    chat_id = message.chat.id
    sessions = dbt.check_session(chat_id)
    bot.send_message(chat_id, f"Доступных сессий у вас: {sessions}")

@bot.message_handler(commands=['new_story'])
@private_access() # это преграждает путь если пользователь не в вайтлисте
def send_genre_keyboard(message):
    chat_id = message.chat.id
    logging.info("Проверка кол-ва сессий")
    current_sessions = dbt.check_session(chat_id)
    if current_sessions == 0:
        bot.send_message(chat_id,"Вы израсходовали все сессии, доступа нету")
    else:
        markup = create_genre_keyboard()
        bot.send_message(message.chat.id, "Краткая сводка по жанрам:\n"
    "- Фэнтези: жанр литературы, в котором используются элементы магии, фантастические существа и мифология для создания волшебных миров и сюжетов.\n"
    "- Научная фантастика: жанр, в котором автор использует научные и технологические концепции для создания футуристических миров и историй, часто затрагивающих вопросы будущего развития человечества.\n"
    "- Детектив: жанр, основанный на расследовании преступлений и разгадывании загадок, часто сосредоточенных на действиях детектива или сыщика.\n"
    "- Боевик: жанр, в котором акцент делается на динамичных сценах схваток и борьбы, преимущественно в контексте физического противостояния и действий героев.")
        bot.send_message(chat_id, "Выберите жанр:", reply_markup=markup)
        current_state[chat_id] = 'genre'
        bot.register_next_step_handler(message, handle_genre_choice)

@bot.message_handler(commands=['begin'])
@private_access()
def begin(message):
    сhat_id = message.chat.id
    if user_sessions.get(сhat_id) == 'waiting_for_command':
        user_sessions[сhat_id] = True
        bot.send_message(сhat_id, "Пожалуйста, введите текст для истории:")
        bot.register_next_step_handler(message, handle_text_message)
    else:
        bot.send_message(сhat_id, 'Вы не начинали истрию, для ее начала предлагаю ввести /new_story')

@bot.message_handler(commands=['end_story'])
def end_history(message):
    global final_choice
    chat_id = message.chat.id
    if chat_id not in user_sessions or not user_sessions[chat_id]:
        bot.send_message(chat_id, "Вы не начали новую историю. Напишите /new_story для начала.")
        return
    user_history = dbh.get_history(message.chat.id)
    history_text = "\n".join([f"{row[0]}: {row[1]} ({row[2]})" for row in user_history])
    text = f"Заверши историю, вот для нее контекст: {history_text}"
    system_text = f"Ты - сценарист, пиши эпос, не расписывай всё до мелчайших деталей, вот общие очертания для истории : {final_choice}"
    final_request = [{"role":"system",
                          "text": system_text},
                        {"role": "user",
                          "text": text}]
    response = gpt_client.create_request(chat_id, final_request)
    if response.status_code == 200:
        try:
            response_json = response.json()
            final_text = response_json['result']['alternatives'][0]['message']['text']
            bot.send_message(chat_id, final_text)
        except KeyError:
            bot.send_message(chat_id, "Извините, не удалось завершить историю.")
    else:
        bot.send_message(chat_id, "Извините, произошла ошибка при завершении истории.")
    # Деактивируем сессию
    user_sessions[chat_id] = False
    dbt.reset_session(chat_id)
    dbh.clear_history(chat_id)
    bot.send_message(chat_id, "История закончена")

@bot.message_handler(func=lambda message: True)
def handle_genre_choice(message):
    global genre, main_person, setting, final_choice
    chat_id = message.chat.id
    if current_state.get(chat_id) == 'genre':
        genre = message.text
        markup = create_character_keyboard()
        bot.send_message(chat_id, f"Жанр: {genre}\nВыберите персонажа:", reply_markup=markup)
        current_state[chat_id] = 'character'
    elif current_state.get(chat_id) == 'character':
        main_person = message.text
        markup = create_setting_keyboard()
        bot.send_message(chat_id, f"Главный герой: {main_person}\nВыберите сеттинг:", reply_markup=markup)
        bot.send_message(chat_id, """Краткая справка по сеттингам:
Постапокалипсис - действия происходят в мире который пережил катастрофу
Пустыня - действия происходят на клочке песка неведомо где, неведомо как
Город - действия происходят в городе, в котором бурлит жизнь""")
        current_state[chat_id] = 'setting'
    elif current_state.get(chat_id) == 'setting':
        setting = message.text
        final_choice = f"Жанр: {genre}, Главный герой: {main_person}, Сеттинг: {setting}"
        current_state[chat_id] = None
        user_sessions[chat_id] = 'waiting_for_command'
        bot.send_message(chat_id,
                         f"Вы сделали выбор:\n{final_choice}\nТеперь, пожалуйста, введите команду /begin", reply_markup=telebot.types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text_message(message):
    if message.text.startswith('/'):
        return
    global final_choice
    chat_id = message.chat.id
    if not user_sessions.get(chat_id, False):
        bot.send_message(chat_id, "Вы не начали новую историю. Напишите /new_story для начала.")
        return
    else:
        current_tokens = dbt.get_tokens(chat_id)
        if current_tokens < 50:
            bot.send_message(chat_id, "Ваши токены закончились. Вы не можете продолжить историю. Вы только можете ее завершить с помощью команды /end_story")
            user_sessions[chat_id] = 'tokens_off_limit'
        else:
            text = message.text # Получаем текст сообщения от пользователя
            user_history = dbh.get_history(message.chat.id)
            history_text = "\n".join([f"{row[0]}: {row[1]} ({row[2]})" for row in user_history])
            logging.info(f"История общения: {history_text}")
            final_text = f"{text}, История чата: {history_text}"
            system_text = f"Ты - сценарист, пиши эпос, не расписывай всё до мелчайших деталей, вот общие очертания для истории: {final_choice}"
            prompt = [{"role":"system",
                              "text": system_text},
                            {"role": "user",
                              "text": final_text}] # Используем текст сообщения как prompt
            tokens_count = gpt_client.count_tokens(final_text)
            dbt.deduct_tokens(chat_id, tokens_count)
            dbt.update_tokens_used(chat_id, tokens_count)
            response = gpt_client.create_request(chat_id, prompt)
            if response.status_code == 200:
                try:
                    response_json = response.json()
                    result_text = response_json['result']['alternatives'][0]['message']['text']
                    logging.info(response_json)
                    bot.send_message(chat_id, result_text)
                    dbh.create_table(chat_id)
                    dbh.save_message(chat_id, 'user', text)
                    dbh.save_message(chat_id, 'assistant', result_text)
                    logging.info(f"История ответа от пользователя {chat_id} сохранена")
                    bot.register_next_step_handler(message, handle_text_message)
                except KeyError:
                    logging.error('Ответ от API GPT не содержит ключа "result"')
                    bot.send_message(chat_id, "Извините, не удалось сгенерировать историю.")
            else:
                logging.error(f'Ошибка API GPT: {response.status_code}')
                bot.send_message(chat_id, f"""
    Извините, произошла ошибка при обращении к API GPT.
    Ошибка: {response.status_code}
    ||Если ошибка 429 - нейросеть просит не так часто писать промпты либо же она нагружена||""",
                             parse_mode='MarkdownV2')
                bot.register_next_step_handler(message, handle_text_message)

if __name__ == "__main__":
    print("Бот запускается...")
    logging.info("Бот запускается...")
    bot.polling()