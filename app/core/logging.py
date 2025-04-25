import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(
    log_file: str,
    level: int = logging.DEBUG,
    http_level: int = logging.INFO,
    max_bytes: int = 32 * 1024 * 1024,
    backup_count: int = 5,
) -> None:
    path = Path(log_file)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Create handler
    handler = RotatingFileHandler(
        filename=path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    handler.setFormatter(
        logging.Formatter(
            fmt="[{asctime}] [{levelname:<8}] {name}: {message}",
            datefmt="%Y-%m-%d %H:%M:%S",
            style="{",
        )
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(handler)

    # Set specific level for discord.http
    # ref: https://discordpy.readthedocs.io/en/stable/logging.html
    logging.getLogger("discord.http").setLevel(http_level)
