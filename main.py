"""
Телеграм бот для мониторинга и удаления спама в группах.
"""

import logging
import sys
from typing import Union
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN, GROUP_IDS
from rules import is_spam, SKIP_ADMINS, SKIP_FORWARDED_MESSAGES, SKIP_CHANNEL_POSTS

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def is_message_from_monitored_chat(chat_id: Union[int, str], chat_username: str = None) -> bool:
    """
    Проверяет, пришло ли сообщение из одного из отслеживаемых чатов.
    
    Args:
        chat_id: ID чата (может быть числом или строкой)
        chat_username: Юзернейм чата (если есть)
        
    Returns:
        bool: True если чат находится в списке отслеживаемых, иначе False
    """
    str_chat_id = str(chat_id)
    
    for group_id in GROUP_IDS:
        # Сравниваем ID чата (как строку)
        if str_chat_id == str(group_id):
            return True
            
        # Если это публичный чат, проверяем username
        if chat_username and isinstance(group_id, str) and group_id.startswith('@'):
            if chat_username == group_id[1:]:  # Убираем @ для сравнения
                return True
                
    return False

async def is_user_admin(context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_id: int) -> bool:
    """
    Проверяет, является ли пользователь администратором чата.
    
    Args:
        context: Контекст бота
        chat_id: ID чата
        user_id: ID пользователя
        
    Returns:
        bool: True если пользователь является администратором или создателем, иначе False
    """
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        # Статусы: 'creator', 'administrator', 'member', 'restricted', 'left', 'kicked'
        return member.status in ('creator', 'administrator')
    except Exception as e:
        logger.error(f"Ошибка при проверке статуса пользователя {user_id}: {e}")
        # В случае ошибки считаем, что пользователь не администратор (безопаснее)
        return False

async def check_and_delete_spam(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Проверяет сообщение на спам и удаляет его, если оно является спамом.
    """
    logger.info(f"Поступило сообщение от пользователя {update.effective_user.id}...")

    # Проверяем, что сообщение из одной из отслеживаемых групп
    chat_id = update.effective_chat.id
    chat_username = getattr(update.effective_chat, 'username', None)
    
    if not is_message_from_monitored_chat(chat_id, chat_username):
        logger.info(f"Сообщение из неотслеживаемого чата {chat_id}...")
        return
    
    # Проверяем, что это не команда бота
    if update.message and update.message.text and update.message.text.startswith('/'):
        logger.info("Распознана команда бота, пропускаем проверку на спам")
        return
    
    # Проверяем, является ли сообщение от имени канала/чата (если настроено)
    if SKIP_CHANNEL_POSTS and update.message and update.message.sender_chat:
        logger.info(f"Сообщение от имени канала/чата {update.message.sender_chat.id}, пропускаем проверку")
        return
    
    # Проверяем, является ли сообщение пересланным (если настроено)
    if SKIP_FORWARDED_MESSAGES and update.message and (update.message.forward_from or update.message.forward_from_chat):
        logger.info("Пересланное сообщение, пропускаем проверку на спам")
        return
    
    # Проверяем, является ли пользователь администратором (если настроено)
    if SKIP_ADMINS and update.effective_user:
        user_id = update.effective_user.id
        if await is_user_admin(context, chat_id, user_id):
            logger.info(f"Пользователь {user_id} является администратором, пропускаем проверку на спам")
            return
    
    # Получаем текст сообщения
    message_text = ""
    if update.message:
        if update.message.text:
            message_text = update.message.text
        elif update.message.caption:
            message_text = update.message.caption
    
    # Проверяем на спам
    logger.info(f"Проверка сообщения на спам: {message_text[:100]}...")

    if message_text and is_spam(message_text):
        try:
            # Удаляем сообщение
            await update.message.delete()
            logger.info(f"Удалено спам-сообщение от пользователя {update.effective_user.id}: {message_text[:50]}...")
            
            # Опционально: можно отправить предупреждение пользователю
            # await context.bot.send_message(
            #     chat_id=update.effective_chat.id,
            #     text=f"@{update.effective_user.username}, пожалуйста, не публикуйте спам!",
            #     reply_to_message_id=update.message.message_id
            # )
            
        except Exception as e:
            logger.error(f"Ошибка при удалении сообщения: {e}")
            # Если не удалось удалить (нет прав или сообщение уже удалено), просто логируем
            pass
    else:
        logger.info(f"правила пройдены")


def main() -> None:
    """Запуск бота."""
    # Проверяем, что токен установлен
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("Пожалуйста, установите BOT_TOKEN в config.py")
        sys.exit(1)
    
    if not GROUP_IDS:
        logger.error("Пожалуйста, установите GROUP_IDS в config.py")
        sys.exit(1)
    
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчик сообщений
    application.add_handler(MessageHandler(filters.ALL, check_and_delete_spam))

    # Выводим информацию о мониторинге
    logger.info(f"Бот запущен. Отслеживаем {len(GROUP_IDS)} чатов: {', '.join(str(g) for g in GROUP_IDS)}")
    
    # Запускаем бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
