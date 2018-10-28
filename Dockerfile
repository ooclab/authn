FROM python:3.7-alpine
MAINTAINER info@ooclab.com

ENV PYTHONIOENCODING=utf-8
ENV PYTHONPATH=/work
ENV PATH /usr/local/bin:$PATH

COPY src /work
COPY requirements.txt .
RUN apk add --no-cache --virtual .pynacl_deps \
  build-base libressl-dev libffi-dev postgresql-dev musl-dev \
  && pip3 install --no-cache-dir -r requirements.txt \
  && python3 -m compileall /work

VOLUME /data
WORKDIR /work

EXPOSE 3000

CMD ["python3", "server.py"]
