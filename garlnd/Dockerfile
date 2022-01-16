FROM python:3.8-slim
MAINTAINER alex@sinyawskiy.ru

RUN apt-get update \
    && apt-get install -qy --no-install-recommends \
    g++ \
    libpq-dev \
    virtualenv \
    && apt-get clean

RUN mkdir /var/log/garlnd/
RUN mkdir /opt/garlnd
COPY . /opt/garlnd
RUN rm /opt/garlnd/garlnd/settings/local.py
WORKDIR /opt/garlnd

RUN virtualenv -ppython3 /opt/garlnd/env
RUN /opt/garlnd/env/bin/pip install -r /opt/garlnd/requirements.txt
#RUN /opt/garlnd/env/bin/python /opt/garlnd/manage.py migrate
#RUN /opt/garlnd/env/bin/python /opt/garlnd/manage.py loaddata fixtures/fixtures.json

EXPOSE 8000

#ENTRYPOINT ["/opt/garlnd/env/bin/python", "/opt/garlnd/manage.py runserver 0.0.0.0:8000"]
