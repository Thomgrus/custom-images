FROM python:3-slim AS build-env
WORKDIR /src/app
COPY backuper.py backuper
ENTRYPOINT [ "python3", "/src/app/backuper" ]
