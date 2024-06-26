from pathlib import Path
import asyncio
import shutil

from aiogram.types import FSInputFile
from loguru import logger

from uploader.settings import settings
from uploader.bot import bot_factory
from core.schemes.movie import kinoclub
from core.schemes.uploader import UploadMovieRequest

TEMP_FOLDER = Path("tempfiles").resolve()


def remove_folder(folder: Path):
    shutil.rmtree(folder, ignore_errors=True)


@logger.catch()
async def download_video(movie: kinoclub.Movie, data: UploadMovieRequest) -> Path:
    folder = TEMP_FOLDER / str(data.get_movie_id())
    if not folder.exists():
        folder.mkdir(0o666, exist_ok=True, parents=True)

    file_path = folder / f"{data.get_movie_id()}.mp4"

    if data.type == "serial":
        seria: kinoclub.Seria = movie.get_seria(data.season, data.seria)
        url = seria.download_url
    else:
        url = movie.download_url

    # Загрузить и преобразовать файл
    process = await asyncio.create_subprocess_exec(
        "yt-dlp", "-f", "bv[height<=720]+wa[language=ru]", "--check-formats", "--user-agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36", "-N", "16",
        "--no-progress", "-o", str(file_path), str(url), stderr=asyncio.subprocess.PIPE
    )
    await process.wait()
    
    logger.info(f"YT-DLP exit: {process.returncode}")
    if process.returncode != 0:
        remove_folder(file_path.parent)
        error = await process.stderr.read()
        raise ValueError(str(error))
    return file_path
    

async def upload_video_to_telegram(movie: kinoclub.Movie, data: UploadMovieRequest, file_path: Path) -> str:
    bot = bot_factory()

    if data.type == "film":
        file = FSInputFile(path=file_path, filename=f"{movie.name}.mp4")
    else:
        file = FSInputFile(path=file_path, filename=f"{movie.name} Сезон: {data.season} Серия: {data.seria}.mp4")

    await bot.send_message(settings.temp_chat_id, f"[Service] Файл {file.filename} загружен, отправляю")
    message = await bot.send_video(
        settings.temp_chat_id, file,
        supports_streaming=True, 
        request_timeout=settings.telegram_timeout,
        width=1280, height=720,
        caption=file.filename.replace(".mp4", "")
    )
    file_id = message.video.file_id
    logger.info(f"FileID: {file_id}")
    await bot.session.close()
    return file_id
