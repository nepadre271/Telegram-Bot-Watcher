import logging
import inspect

from loguru import logger

from bot.settings import settings


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO, force=True)
logging.getLogger('aiogram.event').setLevel(logging.DEBUG)
logging.getLogger('aiogram-dialog').setLevel(logging.DEBUG)
logging.getLogger('aiogram').setLevel(logging.DEBUG)
logger.disable("httpx")

logs_path = settings.pwd / "logs"
logs_path.mkdir(666, exist_ok=True)

logger.add(logs_path / "all.log")
logger.add(logs_path / "payments.log", filter=lambda record: "payments" in record["extra"])
