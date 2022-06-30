async def get_text(local: str, text: str) -> str:
    if local == "ru":
        return ru[text]
    elif local == "en":
        return en[text]
    elif local == "ua":
        return ua[text]
    else:
        return en[text]
    
ru = {
    "hello_text":   "<b>Привет {fname}, я бот для скачивания видео с TikTok </b>" \
                    "\nПросто отправь мне ссылку и я отправлю тебе видео без водяных знаков",
    "error_get_video": "Ошибка при получении видео, выберите другое видео либо попробуйте позже",
    "link_not_recognized": "Не удалось распознать ссылку",
    "error_get_music": "Ошибка при получении музыки, выберите другое видео либо попробуйте позже",
    "error_download": "Ошибка при скачивании, выберите другое видео либо попробуйте позже",
    "loading_video": "⌛Загружаю видео",
    "loading_music": "⌛Загружаю музыку",
    "select_type_download": "Выберите тип загрузки",
    "video": "Видео",
    "audio": "Музыка",
}
ua = {
    "hello_text":   "<b>Привіт {fname}, я бот для скачування відео з TikTok </b> \
                    \nПросто надішліть мені посилання і я відправлю тобі відео без водяних знаків",
    "error_get_video": "Помилка при отриманні відео, виберіть інше відео або спробуйте пізніше",
    "link_not_recognized": "Не вдалося розпізнати посилання",
    "error_get_music": "Помилка при отриманні музики, виберіть інше відео або спробуйте пізніше",
    "error_download": "Помилка при скачуванні, виберіть інше відео або спробуйте пізніше",
    "loading_video": "⌛Завантажую відео",
    "loading_music": "⌛Завантажую музику",
    "select_type_download": "Виберіть тип завантаження",
    "video": "Відео",
    "audio": "Музика",
}
en = {
    "hello_text":   "<b>Hi {fname}, I'm a TikTok video download bot </b>\
                    \nJust send me the link and I'll send you a video without watermark",
    "error_get_video": "Error while getting video, select another video or try later",
    "link_not_recognized": "Couldn't recognize the link",
    "error_get_music": "Error while getting music, select another video or try later",
    "error_download": "Error while downloading, choose another video or try later",
    "loading_video": "⌛Loading video",
    "loading_music": "⌛Loading music",
    "select_type_download": "Select loading type",
    "video": "Video",
    "audio": "Music",
}