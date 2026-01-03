"""
Телеграм бот для мониторинга и удаления спама в группе.
"""

import logging
import sys
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN, GROUP_ID
from rules import is_spam

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def check_and_delete_spam(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Проверяет сообщение на спам и удаляет его, если оно является спамом.
    """

    logger.info(f"Поступило сообщение от пользователя {update.effective_user.id}...")

    # Проверяем, что сообщение из нужной группы
    chat_id = str(update.effective_chat.id)
    group_username = GROUP_ID.replace('@', '')
    if GROUP_ID and chat_id != str(GROUP_ID) and (not update.effective_chat.username or update.effective_chat.username != group_username):
        logger.info(f"неверный чат {chat_id}...")
        return
    
    # Проверяем, что это не команда бота
    if update.message and update.message.text and update.message.text.startswith('/'):
        logger.info(f"распознана команда бота ...")
        return
    
    # Получаем текст сообщения
    message_text = ""
    if update.message:
        if update.message.text:
            message_text = update.message.text
        elif update.message.caption:
            message_text = update.message.caption
    
    # Проверяем на спам
    logger.info(f"Проверка сообщение на спам: {message_text}")

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
    
    if GROUP_ID == "YOUR_GROUP_ID_HERE":
        logger.error("Пожалуйста, установите GROUP_ID в config.py")
        sys.exit(1)
    
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчик для всех сообщений в группах
    # Фильтруем только сообщения в группах и супергруппах
    message_filter = filters.ChatType.GROUPS & ~filters.StatusUpdate.ALL
    
    application.add_handler(MessageHandler(message_filter, check_and_delete_spam))
    
    # Запускаем бота
    logger.info("Бот запущен и готов к работе...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

