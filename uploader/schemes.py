from pydantic import BaseModel


class UploadMovieData(BaseModel):
    file_id: str
    movie_id: int
    

class MovieRequest(BaseModel):
    user_id: str
    movie_id: int
