import httpx

from core.schemes.uploader import UploadMovieRequest


class UploaderService:
    def __init__(self, uploader_url: str):
        self.url = uploader_url

    async def upload_movie(self, data: UploadMovieRequest) -> int:
        async with httpx.AsyncClient(base_url=self.url) as client:
            response = await client.post("/upload", json=data.model_dump())
            return response.status_code
