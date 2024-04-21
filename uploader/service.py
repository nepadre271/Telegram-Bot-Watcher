from pathlib import Path
import logging
import asyncio
import shutil

from aiogram.types import FSInputFile, URLInputFile

from uploader.settings import settings
from uploader.bot import bot_factory
from core.schemes.movie import Movie

logger = logging.getLogger(__name__)
TEMP_FOLDER = Path("tempfiles").resolve()


def remove_folder(folder: Path):
    shutil.rmtree(folder, ignore_errors=True)


async def download_video(movie: Movie) -> Path:
    folder = TEMP_FOLDER / str(movie.id)
    if not folder.exists():
        folder.mkdir(0o666, exist_ok=True, parents=True)

    file_path = folder / f"{movie.id}.mp4"
    
    # Загрузить и преобразовать файл
    process = await asyncio.create_subprocess_exec(
        "yt-dlp", "-f", "bv[height<=720]+wa[language=ru]", "--user-agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36", "-N", "16",
        "--no-progress", "-o", str(file_path), str(movie.download_url), stderr=asyncio.subprocess.PIPE
    )
    await process.wait()
    
    logger.info(f"YT-DLP exit: {process.returncode}")
    if process.returncode != 0:
        remove_folder(file_path.parent)
        raise ValueError(str(process.stderr))
    return file_path
    

async def upload_video_to_telegram(movie: Movie, file_path: Path) -> str:
    bot = bot_factory()
    await bot.send_message(settings.temp_chat_id, f"Файл {movie.name} загружен, отправляю")
    
    file = FSInputFile(path=file_path, filename=f"{movie.name}.mp4")
    message = await bot.send_video(
        settings.temp_chat_id, file,
        supports_streaming=True, 
        request_timeout=settings.telegram_timeout
    )
    file_id = message.video.file_id
    logger.info(f"FileID: {file_id}")
    await bot.close()
    return file_id
