FROM python:3-slim AS build-env
WORKDIR /src/app
RUN pip3 install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip3 install --target=/lib/app -r requirements.txt
COPY backuper.py backuper

FROM gcr.io/distroless/python3
COPY --from=build-env /src/app /src/app
COPY --from=build-env /lib/app /lib/app
ENV PYTHONPATH=/lib/app
WORKDIR /app
ENTRYPOINT [ "python3", "/src/app/backuper" ]
