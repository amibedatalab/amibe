FROM python:3.8-slim

WORKDIR /app

COPY ./requirements.txt ./requirements-dev.txt /app/

RUN apt-get update \
    && apt-get install -y \
        gcc \
        libpq-dev \
        wget \
        git \
        gettext \
        libpq-dev \
        postgresql-client \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements-dev.txt \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get clean \
    && chown -R ${GROUP}:${USER} /var/run/ \
    && wget -O /usr/bin/dumb-init https://github.com/Yelp/dumb-init/releases/download/v1.2.2/dumb-init_1.2.2_amd64 \
    && chmod +x /usr/bin/dumb-init

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
