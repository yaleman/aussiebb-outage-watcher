FROM python:3.11-slim
# FROM python:3.10-alpine

########################################
# add a user so we're not running as root
########################################
RUN useradd useruser


RUN apt-get update
RUN apt-get install -y git
RUN apt-get clean

RUN mkdir -p /home/useruser/.config/
RUN chown useruser /home/useruser -R

RUN mkdir -p build/app

WORKDIR /build

COPY app/ /build/app

COPY poetry.lock .
COPY pyproject.toml .

RUN chown useruser /build -R
WORKDIR /build/
USER useruser

RUN python -m pip install --quiet poetry pytest pyaussiebb
RUN pip install .

CMD python -m app
