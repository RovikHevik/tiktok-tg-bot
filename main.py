#!venv/bin/python
from email.mime import audio
import logging

from multiprocessing.dummy import shutdown
from datetime import datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from tgbot.logic.db import Users, Db
from tgbot.logic.tiktok_scraper import scraper
from tgbot.logic.config import *
from getlocal import *
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
    msg = await get_text(message.from_user.language_code, "hello_text")
    msg = msg.format(fname = message.from_user.full_name)
   
    user = Users(id=message.from_user.id, username=message.from_user.username, first_name=message.from_user.first_name, last_name=message.from_user.last_name, language_code=message.from_user.language_code, is_deleted=False, date=datetime.now())
    await db.write_user(user=user)

    await bot.send_message(message.chat.id, msg)

async def get_keyboard(local_code):
    video = await get_text(local_code, "video")
    audio = await get_text(local_code, "audio")
    buttons = [
                    types.InlineKeyboardButton(text=video, callback_data="video"),
                    types.InlineKeyboardButton(text=audio, callback_data="music"),
                    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard

@dp.message_handler(Text(contains="tiktok"))
async def start_down_dialog(message: types.Message):
    if "http" in message.text:
        id_url[message.from_user.id] = message.text
        user = Users(id=message.from_user.id, username=message.from_user.username, first_name=message.from_user.first_name, last_name=message.from_user.last_name, language_code=message.from_user.language_code, is_deleted=False, date=datetime.now())
        await db.write_user(user=user)
        keyboard = await get_keyboard(message.from_user.language_code)
        msg = await get_text(message.from_user.language_code, "select_type_download")
        await message.answer(msg, reply_markup=keyboard)
    else:
        msg = await get_text(message.from_user.language_code, "link_not_recognized")
        await message.answer(msg)


@dp.message_handler(Text(contains="user"))
async def start_down_dialog(message: types.Message):
    if message.from_user.id == admin_id:
        count = await db.count_user()
        today = await db.count_today_user()
        await message.answer(f"Пользователей в боте: {count} \nСегодня новых: {today}")


@dp.callback_query_handler(Text(startswith="video"))
async def return_video(call: types.CallbackQuery, state: FSMContext):
    video_url = await tiktoke.GetVideoLink(id_url[call.from_user.id])
    msg = await get_text(call.from_user.language_code, "loading_video")
    await call.message.edit_text(msg)
    if video_url == "Ошибка при скачивании":
        msg = await get_text(call.from_user.language_code, "error_get_video")
        await call.message.edit_text(msg)
    else:
        logging.info(f"скачано видео {video_url.filename} пользователем {call.from_user.first_name}")
        await bot.send_video(call.from_user.id, types.InputFile.from_url(url=video_url.url))
        keyboard = await get_keyboard(call.from_user.language_code)
        msg = await get_text(call.from_user.language_code, "select_type_download")
        await call.message.edit_text(msg, reply_markup=keyboard)
        


@dp.callback_query_handler(Text(startswith="music"))
async def return_music(call: types.CallbackQuery,  state: FSMContext):
    music_url = await tiktoke.GetVideoMusic(id_url[call.from_user.id])
    msg = await get_text(call.from_user.language_code, "loading_music")
    await call.message.edit_text(msg)
    if music_url == "Ошибка при скачивании":
        msg = await get_text(call.from_user.language_code, "error_get_music")
        await call.message.edit_text(msg)
    else:
        logging.info(f"скачано аудио {music_url.filename} пользователем {call.from_user.first_name}")
        await bot.send_audio(call.from_user.id, types.InputFile.from_url(url=music_url.url, filename=music_url.filename))
        keyboard = await get_keyboard(call.from_user.language_code)
        msg = await get_text(call.from_user.language_code, "select_type_download")
        await call.message.edit_text(msg, reply_markup=keyboard)



@dp.errors_handler()
async def catch_error(update: types.Update, exception):
    msg = await get_text(update['callback_query']['from']["language_code"], "error_download")
    await bot.send_message(update['callback_query']['from']['id'], msg)
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