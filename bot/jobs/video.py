from pathlib import Path
import subprocess
import logging

from aiogram import types, Bot

from bot.settings import settings
from bot.api import KinoClubAPI
from .base import job_queue

logger = logging.getLogger(__name__)
TEMP_FOLDER = Path("tempfiles").resolve()


@job_queue.task
async def download_video(movie_id: int):
    kinoclub_api = KinoClubAPI(settings.kinoclub_token)
    movie = await kinoclub_api.get_movie(movie_id)

    if not TEMP_FOLDER.exists():
        TEMP_FOLDER.mkdir(0o666, exist_ok=True)

    file_path = TEMP_FOLDER / f"{movie_id}.mp4"

    # Загрузить и преобразовать файл
    try:
        process = subprocess.run([
            "yt-dlp", "--concurrent-fragments", "16", "--no-progress", "--user-agent",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36",
            "-o", str(file_path), str(movie.download_url)
        ])
        logger.info(f"YT-DLP exit: {process.returncode}")
    except Exception as ex:
        logger.info(str(ex))

    return file_path, movie.name


@job_queue.task
async def send_video(bot: Bot, chat_id: int, movie_id: int, movie_name: str):
    # Отправить файл пользователю
    await bot.send_message(chat_id, "Файл загружен, отправляю")
    file_path = TEMP_FOLDER / f"{movie_id}.mp4"
    try:
        file = types.FSInputFile(path=file_path, filename=f"{movie_name}.mp4")
        file_id = await bot.send_video(chat_id, file, supports_streaming=True, request_timeout=settings.tg_timeout)
        logger.info(f"FileID: {file_id}")
    except Exception as ex:
        logger.exception(str(ex))

    # Удалить временный файл
    file_path.unlink(missing_ok=True)
