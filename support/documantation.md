# Политика конфиденциальности
## Предисловие к политике конфиденциальности
- **Пользователь** - человек, который решил воспользоваться ботом
- **Создатель** - человек, который держит бота у хоста, и который написал бота
- **Бот** - сам бот
- **Запросы/Вопросы** - Запросы *пользователя*, которые впоследствии были записаны в базу данных
## Политика конфиденциальности основного бота (https://t.me/YaSpeaking_bot)
1) Бот и его создатель в праве собирать данные о ваших запросах
2) Создатель не несет ответственности за:
   1) Некорректность ответов нейросети 
   2) Некорректность расшифровки вашего запроса
   3) То что бот может не ответить, так как за 5 минут до вашего запроса он чудесным образом лёг
## Политика конфиденциальности тех. поддержки (https://t.me/YaSpeakingSupport_bot)
1) Поддержка не несет цели как-то решить проблему пользователя
2) Создатель в праве делать с вашими вопросами всё что ему взбредет в голову
# Документация и **FAQ**
## Предисловие к документации
- **Пользователь** - человек, который решил воспользоваться ботом
- **Создатель** - человек, который держит бота у хоста, и который написал бота
- **Бот** - сам бот
- **Нейросеть** = **YaGPT**
- **YaGPT/SpeechKit** - сервисы [*YandexCloud*](https://yandex.cloud/ru/?utm_referrer=https%3A%2F%2Fyandex.ru%2F)
- **Токены** - условная единица, которая тратится в обращении к нейросети и считается сервисом, предоставленным *Yandex Cloud*
- **Символы** - условная единица, которая тратится в обращении к SpeechKit, когда пользователь отправил свой запрос к нейросети с помощью голосового сообщения, и надо озвучить сам ответ этой нейросети
- **Блоки** - условная единица, равная 15 секундам, и вне зависимости от продолжения аудио, которое надо расшифровать, его длина будет округлятся в большую сторону (1 секунда = 1 блок, 16 секунд = 2 блока), которая тратится при обращении в SpeechKit на расшифровке аудиосообщения пользователя
## Документация основного бота (https://t.me/YaSpeaking_bot)
### Основные положения
- Бот сделан как финальный проект на курсе *Курс Python в ИИ от Яндекса: разработка ботов на базе нейросетей*
- Бот не требует никаких денежных вложений от пользователя
- Бот работает на серверах Яндекса, так что можете расчитывать на работу 24/7
### Технические положения
- Все запросы бота делаются и производятся на основе сервисов YandexCloud
- Все ошибки и недочеты при ответе нейронки, расшифровки аудиосообщений и озвучивании текста на стороне сервисов YandexCloud
- Вся история запросов хранится в БД
## Документация тех. поддержки (https://t.me/YaSpeakingSupport_bot)
### Основные положения
- Бот написан на коленке, так что на адекватную работу тех. поддержки не расчитывайте
- Бот держится на домашнем ноутбуке, так что на работу 24/7 не стоит расчитывать
### Техничские положения
- Все вопросы и запросы пользователей хранятся в отдельной базе данных
- Ответа на ваш вопрос не стоит ждать
## FAQ
### Почему я не в вайтлисте?
Из-за того что рандомный человек может взять и испаганить весь проект, да так что лимиты не помогут и сдать финальный проект не станет реальным
### Зачем так много писанины, если ее никто не будет читать?
Знал бы кто🤔

# Вроде все
Если вы досюда дошли, то значит вы очень любопытный человек, которому не жалко потратить свое драгоценное время на чтение подобия документации бота, который будет сразу удален после удачной проверки
## Держите Кота Шрёдинегера
![kitek](https://avatars.mds.yandex.net/i?id=1f7da7e49012f672114d70f08ad26afb4f4e7c7d-10752752-images-thumbs&n=13)