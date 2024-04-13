FROM python:3.11.9-slim-bullseye

WORKDIR /app

RUN apt update && apt install ffmpeg -y

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY bot ./bot

CMD ["python", "-m", "bot"]