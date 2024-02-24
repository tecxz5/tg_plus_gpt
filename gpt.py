import requests
from transformers import AutoTokenizer
from config import MAX_TOKENS, GPT_URL, GPT_TOKENAIZER

MAX_LETTERS = MAX_TOKENS
IMPORT_URL = GPT_URL
TOKENAIZER = GPT_TOKENAIZER

class GPT:
    def __init__(self, system_content="Ты - дружелюбный помощник для решения задач по математике. Давай подробный ответ с решением на русском языке"):
        self.system_content = system_content
        self.URL = IMPORT_URL
        self.HEADERS = {"Content-Type": "application/json"}
        self.MAX_TOKENS = MAX_LETTERS
        self.assistant_content = "Ответ вашей задачи: "

    @staticmethod
    def count_tokens(prompt):
        tokenizer = AutoTokenizer.from_pretrained("rhysjones/phi-2-orange")
        return len(tokenizer.encode(prompt))

    def process_resp(self, response):
        if response.status_code <  200 or response.status_code >=  300:
            self.clear_history()
            return False, f"Ошибка: {response.status_code}"

        try:
            full_response = response.json()
        except:
            self.clear_history()
            return False, "Ошибка получения JSON"

        if "error" in full_response or 'choices' not in full_response:
            self.clear_history()
            return False, f"Ошибка: {full_response}"

        result = full_response['choices'][0]['message']['content']

        if result == "":
            self.clear_history()
            return True, "Конец объяснения"

        self.save_history(result)
        return True, self.assistant_content

    def make_promt(self, user_request):
        if user_request == "":
            user_request = "продолжи"
        json = {
            "messages": [
                {"role": "system", "content": self.system_content},
                {"role": "user", "content": user_request},
                {"role": "assistant", "content": self.assistant_content}
            ],
            "temperature":  1.2,
            "max_tokens": self.MAX_TOKENS,
        }
        return json

    def send_request(self, json):
        resp = requests.post(url=self.URL, headers=self.HEADERS, json=json)
        return resp

    def save_history(self, content_response):
        self.assistant_content += content_response

    def clear_history(self):
        self.assistant_content = "Решим задачу по шагам: "