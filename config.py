"""
Конфигурация бота
Использует переменные окружения из файла .env
"""
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

# Токен бота от @BotFather
BOT_TOKEN = os.getenv('BOT_TOKEN', '')

# ID группы (можно получить через @userinfobot или другие боты)
# Может быть числом или строкой (для публичных групп используйте @username)
GROUP_ID = os.getenv('GROUP_ID', '')

# Проверка обязательных переменных
if not BOT_TOKEN or BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
    raise ValueError("Необходимо установить BOT_TOKEN в файле .env")

if not GROUP_ID or GROUP_ID == 'YOUR_GROUP_ID_HERE':
    raise ValueError("Необходимо установить GROUP_ID в файле .env")
