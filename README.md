# Running this


## Build and run
```
docker build -t aussiebb-outage-watcher . 
docker run --rm -it \
    -v "../../.config/aussiebb.json:/home/useruser/.config/aussiebb.json" \
    aussiebb-outage-watcher
```

## Run from github container

```
docker run -d \
    -v "$(pwd)/aussiebb.json:/home/useruser/.config/aussiebb.json" \
    --name outagewatcher --restart always \
    ghcr.io/yaleman/aussiebb-outage-watcher:latest
```
