#!venv/bin/python
import logging
from multiprocessing.dummy import shutdown
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from tgbot.logic.tiktok_scraper import scraper
from aiogram.dispatcher.storage import FSMContext


bot = Bot(token="5443601580:AAHlwKxGGT9_9uZIn4ExOHsBuPOWgnJvjaE", parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)
tiktoke = scraper()
admin_id = 546594574
id_url = {}

@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    msg = f"<b>Привет {message.from_user.full_name}, я бот для скачивания видео с TikTok </b>" \
            "\nПросто отправь мне ссылку и я отправлю тебе видео без водяных знаков"
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
        await message.answer("Выберите тип загрузки", reply_markup=keyboard)
    else:
        await message.answer("Ссылка не распознана")


@dp.callback_query_handler(Text(startswith="video"))
async def return_video(call: types.CallbackQuery, state: FSMContext):
    video_url = await tiktoke.GetVideoLink(id_url[call.from_user.id])
    if video_url == "Ошибка при скачивании":
        await bot.send_message(video_url)
    else:
        await bot.send_video(call.from_user.id, types.InputFile.from_url(url=video_url.url))
        

@dp.callback_query_handler(Text(startswith="music"))
async def return_music(call: types.CallbackQuery,  state: FSMContext):
    music_url = await tiktoke.GetVideoMusic(id_url[call.from_user.id])
    if music_url == "Ошибка при скачивании":
        await bot.send_message(music_url)
    else:
        await bot.send_audio(call.from_user.id, types.InputFile.from_url(url=music_url.url, filename=music_url.filename))


@dp.errors_handler()
async def catch_error(update: types.Update, exception):
    await bot.send_message(admin_id, f"Ошибка в обработке команды \nЮзер с айди: {update['callback_query']['from']['id']} \nОшибка: {exception}")


async def on_startup(dp):
    await bot.send_message(admin_id, "Бот запущен")


async def on_shutdown(dp):
    await bot.send_message(admin_id, "Бот остановлен")
    await shutdown()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_shutdown=on_shutdown, on_startup=on_startup)