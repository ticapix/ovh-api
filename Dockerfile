FROM python:3-alpine

COPY requirements.txt /
COPY run.py /
COPY service /

RUN make install

EXPOSE 8000

CMD ["make", "run"]
