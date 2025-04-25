from app.bot import MyBot
from app.config import settings
from app.utils.logging import setup_logger

setup_logger(log_file="logs/bot.log")


if __name__ == "__main__":
    bot = MyBot()
    bot.run(settings.BOT_TOKEN, log_handler=None)
