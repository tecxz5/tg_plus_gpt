import requests
from transformers import AutoTokenizer
from config import MAX_TOKENS, GPT_URL

MAX_LETTERS = MAX_TOKENS
IMPORT_URL = GPT_URL


class GPT:
    def __init__(self, system_content="Ты - дружелюбный помощник для решения задач по математике. Давай подробный ответ с решением на русском языке"):
        self.system_content = system_content
        self.URL = IMPORT_URL
        self.HEADERS = {"Content-Type": "application/json"}
        self.MAX_TOKENS = MAX_LETTERS
        self.assistant_content = "Решим задачу по шагам: "

    # Подсчитываем количество токенов в промте
    @staticmethod
    def count_tokens(prompt):
        tokenizer = AutoTokenizer.from_pretrained("rhysjones/phi-2-orange")  # название модели
        return len(tokenizer.encode(prompt))

    # Проверка ответа на возможные ошибки и его обработка
    def process_resp(self, response) -> [bool, str]:
        # Проверка статус кода
        if response.status_code < 200 or response.status_code >= 300:
            self.clear_history()
            return False, f"Ошибка: {response.status_code}"

        # Проверка json
        try:
            full_response = response.json()
        except:
            self.clear_history()
            return False, "Ошибка получения JSON"

        # Проверка сообщения об ошибке
        if "error" in full_response or 'choices' not in full_response:
            self.clear_history()
            return False, f"Ошибка: {full_response}"

        # Результат
        result = full_response['choices'][0]['message']['content']

        # Пустой результат == объяснение закончено
        if result == "":
            self.clear_history()
            return True, "Конец объяснения"

        # Сохраняем сообщение в историю
        self.save_history(result)
        return True, self.assistant_content

    # Формирование промта
    def make_promt(self, user_request):
        if user_request == "":
            user_request = "продолжи"
        json = {
            "messages": [
                {"role": "system", "content": self.system_content},
                {"role": "user", "content": user_request},
                {"role": "assistant", "content": self.assistant_content}
            ],
            "temperature": 1.2,
            "max_tokens": self.MAX_TOKENS,
        }
        return json

    # Отправка запроса
    def send_request(self, json):
        resp = requests.post(url=self.URL, headers=self.HEADERS, json=json)
        return resp

    # Сохраняем историю общения
    def save_history(self, content_response):
        self.assistant_content += content_response

    # Очистка истории общения
    def clear_history(self):
        self.assistant_content = "Решим задачу по шагам: "

