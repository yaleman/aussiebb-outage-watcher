FROM python:3.13-slim

########################################
# add a user so we're not running as root
########################################
RUN useradd useruser


RUN apt-get update
RUN apt-get install -y git
RUN apt-get clean

RUN mkdir -p /home/useruser/.config/
RUN chown useruser /home/useruser -R

RUN mkdir -p build/aussiebb_outage_watcher

WORKDIR /build

COPY aussiebb_outage_watcher/* /build/aussiebb_outage_watcher

COPY uv.lock .
COPY pyproject.toml .

RUN chown useruser /build -R
WORKDIR /build/
USER useruser

RUN python -m pip install --no-cache --quiet uv
RUN pip install .

WORKDIR /home/useruser

CMD [".local/bin/aussiebb-outage-watcher"]
