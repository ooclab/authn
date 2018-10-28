FROM python:3.7-alpine
MAINTAINER info@ooclab.com

ENV PYTHONIOENCODING=utf-8
ENV PYTHONPATH=/work
ENV PATH /usr/local/bin:$PATH

COPY requirements.txt .
RUN apk add --no-cache --virtual .pynacl_deps \
  gcc libc-dev libressl-dev libffi-dev \
  && pip3 install --no-cache-dir -r requirements.txt \
  && python3 -m compileall /work
COPY src /work

VOLUME /data
WORKDIR /work

EXPOSE 3000

CMD ["python3", "server.py"]
