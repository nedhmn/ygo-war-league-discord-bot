import logging

from app.bot import MyBot
from app.core.config import settings
from app.core.logging import setup_logger

setup_logger(
    log_file="logs/bot.log",
    level=logging.DEBUG if settings.ENVIORNMENT == "local" else logging.INFO,
)


if __name__ == "__main__":
    bot = MyBot()
    bot.run(token=settings.BOT_TOKEN, log_handler=None)
