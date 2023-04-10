# first stage
FROM python:3.8-slim-buster as builder

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8050

CMD ["python3", "index.py"]


