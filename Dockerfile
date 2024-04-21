FROM python:3.11.9-slim-bullseye

WORKDIR /app

RUN apt update && apt install ffmpeg -y

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./
EXPOSE 8000
ENV PYTHONPATH "${PYTHONPATH}:/app"

CMD ["python", "-m", "bot"]