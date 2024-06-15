import inspect
import logging

from loguru import logger


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

        message = record.getMessage()
        logger.opt(depth=depth, exception=record.exc_info).log(level, f"{record.name}: {message}")


logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
logging.getLogger("taskiq.dependencies.ctx").setLevel(logging.ERROR)

logger.disable("taskiq.kicker")
logger.disable("taskiq.receiver.receiver")
logger.disable("taskiq.receiver.params_parser")
logger.disable("httpx._client")
logger.disable("httpx._config")
logger.disable("httpcore._trace")
