import asyncio
import logging
import os
import threading
from pathlib import Path

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile
from aiogram.exceptions import TelegramAPIError

from flask import Flask
from waitress import serve


# ==============================
# НАСТРОЙКИ
# ==============================

BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", "8080"))

PHOTO_PATH = (
    Path(file).resolve().parent
    / "IMG_20261115_022738.jpg"
)

CAPTION = (
    "Переходи, тут розыгрыши и раздачи! 🎁\n"
    "Также можно выиграть NFT-подарок.\n\n"
    "👇👇👇👇👇👇👇👇\n"
    "https://t.me/lovipodarochki"
)


# ==============================
# ЛОГИРОВАНИЕ
# ==============================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(name)


# ==============================
# ПРОВЕРКА ТОКЕНА
# ==============================

if not BOT_TOKEN:
    raise RuntimeError(
        "ОШИБКА: добавь BOT_TOKEN в переменные окружения Render!"
    )


# ==============================
# TELEGRAM
# ==============================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: types.Message):
    try:
        if PHOTO_PATH.exists():

            photo = FSInputFile(str(PHOTO_PATH))

            await message.answer_photo(
                photo=photo,
                caption=CAPTION
            )

        else:
            logger.error(
                "Фотография не найдена: %s",
                PHOTO_PATH
            )

            await message.answer(
                "Привет! 👋\n\n" + CAPTION
            )

    except TelegramAPIError:
        logger.exception("Ошибка отправки сообщения")

        await message.answer(
            "Не удалось отправить сообщение. Попробуй ещё раз."
        )


# ==============================
# FLASK
# ==============================

app = Flask(name)


@app.get("/")
def health_check():
    return "OK - Telegram bot is running!", 200


@app.get("/health")
def health():
    return {"status": "online"}, 200


# ==============================
# ЗАПУСК БОТА
# ==============================

def run_bot():
    try:
        asyncio.run(
            dp.start_polling(
                bot,
                handle_signals=False
            )
        )

    except Exception:
        logger.exception(
            "Критическая ошибка Telegram-бота"
        )


# ==============================
# ЗАПУСК ПРИЛОЖЕНИЯ
# ==============================

if name == "main":

    logger.info("Запуск Telegram-бота...")

    bot_thread = threading.Thread(
        target=run_bot,
        name="telegram-bot",
        daemon=True
    )

    bot_thread.start()

    logger.info(
        "Запуск Flask на порту %s...",
        PORT
    )

    try:
        serve(
            app,
            host="0.0.0.0",
            port=PORT
        )

    finally:
        logger.info("Завершение приложения...")
