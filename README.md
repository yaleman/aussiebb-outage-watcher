# Running this

## Build and run

```shell
mise run docker
docker run --rm -it \
    -v "$HOME/.config/aussiebb.json:/home/useruser/.config/aussiebb.json" \
    ghcr.io/yaleman/aussiebb-outage-watcher:latest
```

## Run from github container

```shell
docker run -d \
    -v "$(pwd)/aussiebb.json:/home/useruser/.config/aussiebb.json" \
    --name outagewatcher --restart always \
    ghcr.io/yaleman/aussiebb-outage-watcher:latest
```
