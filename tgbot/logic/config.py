import configparser
from dataclasses import dataclass


@dataclass
class TgBot:
    bot_token: str
    db_url: str
    admin_id: int

@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str):
    config = configparser.ConfigParser()
    config.read(path)

    tg_bot = config["tg_bot"]

    return Config(
        tg_bot=TgBot(
            bot_token=tg_bot["bot_token"],
            db_url=tg_bot["db_url"],
            admin_id=int(tg_bot["admin_id"])
        )
    )
