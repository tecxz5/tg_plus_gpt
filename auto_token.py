import configparser
import requests

# Функция для получения токена
def get_token() -> str:
    url = "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token"
    headers = {"Metadata-Flavor": "Google"}
    response = requests.request("GET", url, headers=headers)
    return response.json()["access_token"]

# Получаем токен
new_token = get_token()

# Создаем объект configparser
config = configparser.ConfigParser()

# Читаем существующий файл config.py
config.read('config.py')

# Перезаписываем значение TOKEN новым токеном
config['DEFAULT']['IAM_TOKEN'] = new_token

# Записываем изменения в файл config.py
with open('config.py', 'w') as configfile:
    config.write(configfile)

print("Токен успешно перезаписан в config.py")