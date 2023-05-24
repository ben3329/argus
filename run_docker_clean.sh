#!/bin/bash
docker-compose down
rm -rf database-data/*
rm -rf logs/*
rm -rf argus/monitoring/migrations
docker-compose up -d