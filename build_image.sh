#!/bin/bash
cd argus
DOCKER_BUILDKIT=1 docker build -t argus:latest .
cd ../scrape
DOCKER_BUILDKIT=1 docker build -t scrape:latest .
