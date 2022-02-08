FROM python:3.10-slim
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

RUN git clone https://github.com/yaleman/pyaussiebb.git
RUN git -C pyaussiebb checkout outages
RUN python -m pip install --quiet poetry pytest

RUN python -m pip install --quiet ./pyaussiebb
RUN python -m pip install --quiet --upgrade .

CMD python -m app
