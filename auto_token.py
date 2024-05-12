import requests
import schedule
import time


def get_token() -> str:
    url = "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token"
    headers = {"Metadata-Flavor": "Google"}
    response = requests.request("GET", url, headers=headers)
    return response.json()["access_token"]


def update_config_file(file_path):
    # Чтение содержимого файла
    with open(file_path, 'r') as file:
        content = file.read()

    # Получение нового токена
    new_token = get_token()

    # Замена старого токена на новый
    content = content.replace('IAM_TOKEN = "old_token_value"', f'IAM_TOKEN = "{new_token}"')

    # Перезапись файла с новым содержимым
    with open(file_path, 'w') as file:
        file.write(content)


# Планирование обновления каждые 8 часов
schedule.every(8).hours.do(update_config_file, 'config.py')

while True:
    # Проверяем и выполняем задачи, которые должны быть выполнены
    schedule.run_pending()
    time.sleep(1)