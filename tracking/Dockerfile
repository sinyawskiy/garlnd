FROM python:3.8-slim
MAINTAINER alex@sinyawskiy.ru

RUN apt-get update -qy
RUN apt-get install supervisor -qy
RUN apt-get install virtualenv -qy
RUN apt-get -qy autoremove

ADD ./docker_files/tracking_supervisor.conf /etc/supervisor/conf.d/supervisord.conf

RUN mkdir /opt/tracking -p
RUN mkdir /var/log/tracking -p
COPY . /opt/tracking
WORKDIR /opt/tracking
RUN virtualenv -ppython3 /opt/tracking/env
RUN /opt/tracking/env/bin/pip install -r requirements.txt

EXPOSE 6006 5005 12300

ENTRYPOINT ["/usr/bin/supervisord"]
