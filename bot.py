import telebot
import logging
from telebot import types
from functools import wraps
from gpt import PyYandexGpt
from database_token import Database
from config import TOKEN, WHITELISTED_USERS, GPT_TOKEN, GPT_URL

bot = telebot.TeleBot(TOKEN)
dbt = Database("tokens.db")
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

@bot.message_handler(commands=['used_tokens'])
def used_tokens_handler(message):
    chat_id = message.chat.id
    tokens_used = dbt.get_tokens_used(chat_id)
    bot.send_message(chat_id, f"Вы потратили {tokens_used} токенов.")

@bot.message_handler(commands=['new_story'])
@private_access() # это преграждает путь если пользователь не в вайтлисте
def send_genre_keyboard(message):
    chat_id = message.chat.id
    user_sessions[chat_id] = True
    markup = create_genre_keyboard()
    bot.send_message(message.chat.id, "Краткая сводка по жанрам:\n"
"- Фэнтези: жанр литературы, в котором используются элементы магии, фантастические существа и мифология для создания волшебных миров и сюжетов.\n"
"- Научная фантастика: жанр, в котором автор использует научные и технологические концепции для создания футуристических миров и историй, часто затрагивающих вопросы будущего развития человечества.\n"
"- Детектив: жанр, основанный на расследовании преступлений и разгадывании загадок, часто сосредоточенных на действиях детектива или сыщика.\n"
"- Боевик: жанр, в котором акцент делается на динамичных сценах схваток и борьбы, преимущественно в контексте физического противостояния и действий героев.")
    bot.send_message(chat_id, "Выберите жанр:", reply_markup=markup)
    current_state[chat_id] = 'genre'

@bot.message_handler(commands=['end_story'])
def end_history(message):
    chat_id = message.chat.id
    if chat_id not in user_sessions or not user_sessions[chat_id]:
        bot.send_message(chat_id, "Вы не начали новую историю. Напишите /new_story для начала.") # горжусь этой функцией
        return
    user_sessions[chat_id] = False
    dbt.reset_session(chat_id)
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
        current_state[chat_id] = 'setting'
    elif current_state.get(chat_id) == 'setting':
        setting = message.text
        final_choice = f"Жанр: {genre}, Главный герой: {main_person}, Сеттинг: {setting}"
        current_state[chat_id] = None
        bot.send_message(chat_id,
                         f"Вы сделали выбор:\n{final_choice}\nТеперь, пожалуйста, введите текст для истории:")
        bot.register_next_step_handler(message, handle_text_message)

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text_message(message):
    global final_choice
    chat_id = message.chat.id
    if chat_id not in user_sessions or not user_sessions[chat_id]:
        bot.send_message(chat_id, "Вы не начали новую историю. Напишите /new_story для начала.") # горжусь этой функцией
        return
    else:
        text = message.text # Получаем текст сообщения от пользователя
        system_text = f"Ты - сценарист, пиши эпос, вот общие очертания для истории: {final_choice}"
        prompt = [{"role":"system",
                          "text": system_text},
                        {"role": "user",
                          "text": text}] # Используем текст сообщения как prompt
        tokens_count = gpt_client.count_tokens(text)
        dbt.deduct_tokens(chat_id, tokens_count)
        dbt.update_tokens_used(chat_id, tokens_count)
        logging.info(f"Кол-во токенов: {tokens_count}")
        system_tokens_count = gpt_client.count_tokens(system_text)
        dbt.deduct_tokens(chat_id, system_tokens_count)
        dbt.update_tokens_used(chat_id, system_tokens_count)
        logging.info(f"Кол-во токенов в затраченных в System: {system_tokens_count}")
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
||Если ошибка 429 - нейросеть просит не так часто писать промпты либо же она нагружена||""",
                         parse_mode='MarkdownV2')

if __name__ == "__main__":
    print("Бот запускается...")
    logging.info("Бот запускается...")
    bot.polling()