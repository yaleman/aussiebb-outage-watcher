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
docker build -t aussiebb-outage-watcher . 
docker run --rm -it \
    -v "./aussiebb.json:/home/useruser/.config/aussiebb.json" \
    ghcr.io/yaleman/aussiebb-outage-watcher
```
