FROM osgeo/gdal:ubuntu-small-latest

WORKDIR /usr/src/app
COPY . .

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    && apt-get install -y software-properties-common && apt-get update \
    && apt-get install -y python3 python3-pip \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip

RUN export CPLUS_INCLUDE_PATH=/usr/include/gdal
RUN export C_INCLUDE_PATH=/usr/include/gdal
RUN pip install gdal
RUN pip install -r requirements.txt

EXPOSE 8888

CMD python main.py
