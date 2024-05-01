from pydantic import BaseModel


class UploadMovieData(BaseModel):
    file_id: str
    movie_id: str
