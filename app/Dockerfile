FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5051

CMD ["python", "main.py"]