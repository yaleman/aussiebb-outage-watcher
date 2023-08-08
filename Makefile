.DEFAULT: container

.PHONY: container

container:
	docker build -t ghcr.io/yaleman/aussiebb-outage-watcher:latest .
