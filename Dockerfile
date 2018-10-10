FROM python:3-alpine

COPY requirements.txt /
COPY run.py /
COPY service /

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["python", "run.py"]
