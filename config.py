"""
Конфигурация бота
Использует переменные окружения из файла .env
"""
import os
from dotenv import load_dotenv
from typing import List, Union

def get_group_ids() -> List[Union[int, str]]:
    """Получает список ID чатов из переменных окружения."""
    group_ids = os.getenv('GROUP_IDS', '')
    if not group_ids:
        return []
    
    result = []
    for group_id in group_ids.split(','):
        group_id = group_id.strip()
        if group_id.isdigit():
            result.append(int(group_id))
        else:
            result.append(group_id)
    return result

# Загружаем переменные окружения из файла .env
load_dotenv()

# Токен бота от @BotFather
BOT_TOKEN = os.getenv('BOT_TOKEN', '')

# Список ID чатов для мониторинга (через запятую)
# Могут быть числами (для приватных чатов) или строками (для публичных групп, используйте @username)
GROUP_IDS = get_group_ids()

# Проверка обязательных переменных
if not BOT_TOKEN or BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
    raise ValueError("Необходимо установить BOT_TOKEN в файле .env")

if not GROUP_IDS:
    raise ValueError("Необходимо указать хотя бы один чат в переменной GROUP_IDS в файле .env")
