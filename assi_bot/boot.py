from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import TOKEN
WEB_APP_URL = 'url'

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

@dp.message_handler(commands=['start'])
async def start_buttons(message: types.Message):
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            text="Open Web App",
            web_app=types.WebAppInfo(url=WEB_APP_URL)
        )
    )
    await message.answer(
        "Click the button below to open the web app:",
        reply_markup=keyboard
    )

if __name__ == '__main__':
    executor.start_polling(dp)