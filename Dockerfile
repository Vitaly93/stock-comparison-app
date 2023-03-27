# first stage
FROM python:3.8-slim-buster as builder

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "index.py"]


