FROM python:3-alpine

RUN apt-get update && apt-get install -y --no-install-recommends make

COPY requirements.txt /
COPY run.py /
COPY service /

RUN make install

EXPOSE 8000

CMD ["make", "run"]
