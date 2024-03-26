import enum
import requests
import logging
from config import GPT_TOKEN, GPT_URL

logger = logging.getLogger(__name__)
logging.basicConfig(filename='bot_logs.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')  # логер

class Role(enum.StrEnum):
    assistant = "assistant",
    user = "user",
    system = "system"

def get_token() -> str:
    url = "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token"
    headers = {"Metadata-Flavor": "Google"}
    response = requests.request("GET", url, headers=headers)
    return response.json()["access_token"]

class YandexGptError(Exception):
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def __new__(*args, **kwargs):
        pass


class Prompt:
    def __init__(self, role: Role, prompt: str):
        self.role = role
        self.prompt = prompt

    def to_dict(self):
        return {"role": self.role, "prompt": self.prompt}


class PyYandexGpt:
    def __init__(self, token, folder_id: str, gpt: str):
        self.token = GPT_TOKEN
        self.folder_id = GPT_URL
        self.gpt = 'yandexgpt-lite'
        self.history = {}



    def add_history(self, role: Role, text: str, user_id: int) -> None:
        if user_id not in self.history:
            self.history[user_id] = []
        self.history[user_id].append(Prompt(role, text))

    def clear_history(self, user_id) -> None:
        if user_id not in self.history:
            return

        self.history[user_id] = []

    def get_history(self, user_id: int) -> [Prompt]:
        return self.history[user_id]

    def create_request(self, user_id: int, prompt: str) -> requests.Response:
        url = f"https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        data = {
            "modelUri": f"gpt://{self.folder_id}/{self.gpt}/latest",
            "completionOptions": {
                "stream": False,
                "temperature": 0.6,
                "maxTokens": "200"
            },
            "messages": prompt
        }

        # Логирование данных запроса
        logging.debug(f"Отправляем запрос к API GPT с данными: {data}")
        return requests.request("POST", url, json=data, headers=headers)

    def response(self, rep: requests.Response, user_id: int) -> dict:
        if rep.status_code != 200:
            raise YandexGptError("Response status code: " + str(rep.status_code))

        try:
            if "error" not in rep.json():
                result = rep.json()['result']['alternatives'][0]['message']['text']
                token = rep.json()['result']['usage']['totalTokens']
            else:
                if rep.json()['error']["message"] == "The token is invalid" or rep.json()['error']["message"] == "IAM token or API key has to be passed in request":
                    self.token = get_token()
                    self.create_request(user_id)
                    return {}
                else:
                    raise YandexGptError(rep.json()['error']["message"])
        except Exception as e:
            raise YandexGptError(e)

        self.add_history(Role.assistant, result, user_id)

        return {"result": result, "tokens": token}

    def count_tokens(self, text: str) -> int:
        token = self.token
        folder_id = self.folder_id
        headers = {  # заголовок запроса, в котором передаем IAM-токен
            'Authorization': f'Bearer {token}',  # token - наш IAM-токен
            'Content-Type': 'application/json'
        }
        data = {
            "modelUri": f"gpt://{folder_id}/yandexgpt/latest",  # указываем folder_id
            "maxTokens": "500",
            "text": text  # text - тот текст, в котором мы хотим посчитать токены
        }
        return len(
            requests.post(
                "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenize",
                json=data,
                headers=headers
            ).json()['tokens']
        )
        try:
            logging.info(f"Ответ от counter tokens: {len(json)}")
            tokens = response.json().get('tokens', [])
            return len(tokens)
        except KeyError:
            print("Ошибка: ключ 'tokens' не найден в ответе API.")
            return 0