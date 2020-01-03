FROM python:3-alpine
RUN apk add build-base

RUN mkdir /app

WORKDIR /app

COPY requirements.txt .
COPY run.py .
COPY service ./service

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["python", "run.py"]
