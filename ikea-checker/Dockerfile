FROM python:3-slim AS build-env
WORKDIR /src/app

RUN pip3 install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY app.py app.py
ENTRYPOINT [ "python3", "/src/app/app.py" ]
