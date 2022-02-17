FROM python:3-slim
WORKDIR /src/app

# LANG
RUN apt-get update
RUN apt-get install -y locales
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/fr_FR.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LC_ALL fr_FR.UTF-8 
ENV LANG fr_FR.UTF-8  
ENV LANGUAGE fr_FR:fr

RUN pip3 install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt
COPY programme.py programme-tnt

ENTRYPOINT [ "python3", "/src/app/programme-tnt" ]
