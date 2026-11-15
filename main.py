import asyncio
import os
import threading

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from flask import Flask
from waitress import serve

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
app = Flask(__name__)


@dp.message(CommandStart())
async def start_handler(message: types.Message):
    photo = types.FSInputFile("IMG_20261115_022738.jpg")
    caption = (
        "Переходи, тут розыгрыши, и раздачи, так же можно выиграть NFT подарок\n"
        "👇👇👇👇👇👇👇👇\n"
        "https://t.me/lovipodarochki"
    )
    await message.answer_photo(photo=photo, caption=caption)


async def main():
    await dp.start_polling(bot, handle_signals=False)


@app.get("/")
def health_check():
    return "OK", 200


def run_bot():
    asyncio.run(main())


if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot, name="telegram-bot", daemon=True)
    bot_thread.start()

    port = int(os.environ.get("PORT", "8080"))
    serve(app, host="0.0.0.0", port=port)
