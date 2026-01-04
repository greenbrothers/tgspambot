# Правила для определения спама
# Каждое правило - это регулярное выражение
# Если сообщение соответствует хотя бы одному правилу, оно считается спамом

import re

# Настройки фильтрации сообщений
# Если True, сообщения от администраторов не будут проверяться на спам
SKIP_ADMINS = True

# Если True, пересланные сообщения не будут проверяться на спам
SKIP_FORWARDED_MESSAGES = True

# Если True, сообщения от имени канала/чата (sender_chat) не будут проверяться на спам
SKIP_CHANNEL_POSTS = True

# Список правил (регулярные выражения)
SPAM_RULES = [
    # Примеры правил - раскомментируйте и настройте под свои нужды
    
    # Ссылки на подозрительные домены
    r'https?://(?:bit\.ly|tinyurl|t\.co|goo\.gl|short\.link)',
    
    # Криптовалютные мошенничества
    r'(?:bitcoin|btc|ethereum|eth|crypto).*(?:free|giveaway|double|multiply)',
    
    # Подозрительные предложения денег
    r'(?:заработок|зарплата|деньги).*(?:быстро|легко|без вложений)',
    
    # Спам с повторяющимися символами
    r'(.)\1{10,}',  # Один символ повторяется 11+ раз
    
    # Капслок (более 50% заглавных букв в словах)
    # Это правило будет проверяться отдельно в коде
    
    # Подозрительные комбинации символов
    r'[!@#$%^&*()_+=\[\]{}|;:,.<>?]{5,}',  # Много спецсимволов подряд
    
    # Ссылки на файлообменники
    r'https?://(?:mega\.nz|mediafire|dropbox|drive\.google)',
    
    # Любые упоминания пользователей
    # r'@\w+',
    
    # Добавьте свои правила здесь
    # Пример: r'ваш_паттерн'
    r'@Astrixesmoonbot',

]

# Компилируем регулярные выражения для лучшей производительности
COMPILED_RULES = [re.compile(rule, re.IGNORECASE | re.UNICODE) for rule in SPAM_RULES]


def is_spam(text: str) -> bool:
    """
    Проверяет, является ли текст спамом на основе правил.
    
    Args:
        text: Текст сообщения для проверки
        
    Returns:
        True, если текст является спамом, False иначе
    """
    if not text:
        return False
    
    # Проверка по регулярным выражениям
    for rule in COMPILED_RULES:
        if rule.search(text):
            return True
    
    # Проверка на капслок (более 50% заглавных букв в словах)
    words = text.split()
    if words:
        caps_count = sum(1 for word in words if word.isupper() and len(word) > 1)
        if caps_count / len(words) > 0.5:
            return True
    
    # Проверка на слишком короткие сообщения с множеством ссылок
    url_pattern = re.compile(r'https?://\S+')
    urls = url_pattern.findall(text)
    if len(urls) > 2 and len(text) < 100:
        return True


    return False

