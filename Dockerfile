FROM python:3.9-slim

WORKDIR /usr/src/app
COPY . .

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    && apt-get install -y binutils libproj-dev gdal-bin \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/* \
    && python -m pip install --upgrade pip \
    && pip install -r requirements.txt

EXPOSE 8888

CMD jupyter notebook