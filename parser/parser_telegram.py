from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
import logging
from pymongo import MongoClient

from config import API_KEY_MONGO
from middleware_json import middleware

API_TOKEN = 'placeholder'
CHAT_ID = 'placeholder'
TARGET_USER_ID = 'placeholder'
ADMIN_ID = 'placeholder' 

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)

# Подключение к MongoDB
cluster = MongoClient(API_KEY_MONGO)

db = cluster['Assi']
collection = db['assi_datalake']


#the state of listening

listening_state = {}

#that func is listening the buttons

@dp.message_handler(commands=['start'])
async def start_buttons(message: types.Message):
    keyboard_start_stop = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Старт", callback_data='start'),
        InlineKeyboardButton("Стоп", callback_data='stop')
    )
    await message.answer(
        f'Здравствуйте, *{message.from_user.first_name}*!\n\nНажмите "Старт" для начала или "Стоп" для остановки.',
        reply_markup=keyboard_start_stop,
        parse_mode='Markdown'
    )

#that func enable the listening session

@dp.callback_query_handler(lambda c: c.data == 'start')
async def start_parsing(callback_query: types.CallbackQuery):

    global listening_state
    listening_state[callback_query.from_user.id] = True

    logging.info(f"Started listening to messages from user {callback_query.from_user.id}")
    
    await bot.send_message(
        callback_query.from_user.id,
        "Started listening!"
    )

#that func disable the listening session

@dp.callback_query_handler(lambda c: c.data == 'stop')
async def stop_parsing(callback_query: types.CallbackQuery):

    global listening_state
    listening_state[callback_query.from_user.id] = False

    logging.info(f"Stopped listening to messages from user {callback_query.from_user.id}")

    await bot.send_message(
        callback_query.from_user.id,
        "Stopped listening!"
    )

#handling functions

@dp.message_handler(lambda message: message.from_user.id == TARGET_USER_ID)
async def handle_message_from_target_user(message: types.Message):
    chat_id_str = str(message.chat.id)
    if chat_id_str.startswith('-100'):
        chat_id_str = chat_id_str[4:] 


    message_link = f"https://t.me/c/{chat_id_str}/{message.message_id}"

    msg_text = message.text

    if len(msg_text.split('\n')) > 1:
        msg_text = msg_text.split('\n')[0]


    try:
        result = collection.insert_one({
            'user_id': message.from_user.id,
            'message_id': message.message_id,
            'message_text': msg_text,
            'message_link': message_link,
            'article': middleware(msg_text)
        })
        logging.info(f"Сообщение {message.message_id} успешно сохранено в MongoDB. ID вставленного документа: {result.inserted_id}.")
    except Exception as e:
        logging.error(f"Ошибка при сохранении сообщения в MongoDB: {e}")

    try:
        await bot.send_message(
            ADMIN_ID,
            f"Ссылка на сообщение: {message_link}\n\nТекст сообщения: {msg_text}\n\nЗаголовок: {middleware(msg_text)}"
        )
        logging.info(f"Ссылка и текст сообщения успешно пересланы админу {ADMIN_ID}.")
    except Exception as e:
        logging.error(f"Ошибка при пересылке ссылки и текста админу: {e}")

#that func redirect the message to admin

@dp.message_handler(lambda message: message.chat.id == CHAT_ID and message.from_user.id == TARGET_USER_ID)
async def handle_message_from_target_user(message: types.Message):

    global listening_state
    if listening_state.get(message.from_user.id):
        msg = message.text
        try:
            await bot.send_message(ADMIN_ID, f"Получено сообщение от пользователя {message.from_user.id}: {msg}")
            logging.info(f"Сообщение успешно переслано админу {ADMIN_ID}.")
        except Exception as e:
            logging.error(f"Ошибка при пересылке сообщения админу: {e}")

if __name__ == '__main__':
    logging.info("Bot is starting...")
    executor.start_polling(dp, skip_updates=True)