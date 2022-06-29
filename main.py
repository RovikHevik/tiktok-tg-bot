#!venv/bin/python
import logging

from multiprocessing.dummy import shutdown
from datetime import datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from tgbot.logic.db import Users, Db
from tgbot.logic.tiktok_scraper import scraper
from tgbot.logic.config import *
from aiogram.dispatcher.storage import FSMContext


logging.basicConfig(level=logging.INFO)
config = load_config("bot.ini")

bot = Bot(token=config.tg_bot.bot_token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

db = Db()

tiktoke = scraper()
admin_id = config.tg_bot.admin_id
id_url = {}

@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    msg = f"<b>Привет {message.from_user.full_name}, я бот для скачивания видео с TikTok </b>" \
            "\nПросто отправь мне ссылку и я отправлю тебе видео без водяных знаков"
   
    user = Users(id=message.from_user.id, username=message.from_user.username, first_name=message.from_user.first_name, last_name=message.from_user.last_name, language_code=message.from_user.language_code, is_deleted=False, date=datetime.now())
    await db.write_user(user=user)

    await bot.send_message(message.chat.id, msg)

@dp.message_handler(Text(contains="tiktok"))
async def start_down_dialog(message: types.Message):
    if "http" in message.text:
        buttons = [
                    types.InlineKeyboardButton(text="Видео", callback_data="video"),
                    types.InlineKeyboardButton(text="Аудио", callback_data="music"),
                    ]
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(*buttons)
        id_url[message.from_user.id] = message.text
        user = Users(id=message.from_user.id, username=message.from_user.username, first_name=message.from_user.first_name, last_name=message.from_user.last_name, language_code=message.from_user.language_code, is_deleted=False, date=datetime.now())
        await db.write_user(user=user)
        await message.answer("Выберите тип загрузки", reply_markup=keyboard)
    else:
        await message.answer("Ссылка не распознана")


@dp.message_handler(Text(contains="user"))
async def start_down_dialog(message: types.Message):
    if message.from_user.id == admin_id:
        count = await db.count_user()
        await message.answer(f"Пользователей в боте: {count}")


@dp.callback_query_handler(Text(startswith="video"))
async def return_video(call: types.CallbackQuery, state: FSMContext):
    video_url = await tiktoke.GetVideoLink(id_url[call.from_user.id])
    if video_url == "Ошибка при скачивании":
        await bot.send_message(video_url)
    else:
        logging.info(f"скачано видео {video_url.filename} пользователем {call.from_user.first_name}")
        await bot.send_video(call.from_user.id, types.InputFile.from_url(url=video_url.url))
        

@dp.callback_query_handler(Text(startswith="music"))
async def return_music(call: types.CallbackQuery,  state: FSMContext):
    music_url = await tiktoke.GetVideoMusic(id_url[call.from_user.id])
    if music_url == "Ошибка при скачивании":
        await bot.send_message(music_url)
    else:
        logging.info(f"скачано аудио {music_url.filename} пользователем {call.from_user.first_name}")
        await bot.send_audio(call.from_user.id, types.InputFile.from_url(url=music_url.url, filename=music_url.filename))


@dp.errors_handler()
async def catch_error(update: types.Update, exception):
    await bot.send_message(update['callback_query']['from']['id'], "Ошибка, выберете другое видео")
    await bot.send_message(admin_id, f"Ошибка в обработке команды \nЮзер с айди: {update['callback_query']['from']['id']} \nОшибка: {exception}")


async def on_startup(dp):
    await bot.send_message(admin_id, "Бот запущен")
    await db.connect(config.tg_bot.db_url)
    await db.create_db()


async def on_shutdown(dp):
    await bot.send_message(admin_id, "Бот остановлен")
    await shutdown()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_shutdown=on_shutdown, on_startup=on_startup)