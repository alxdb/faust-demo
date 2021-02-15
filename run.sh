#!/usr/bin/env sh

docker-compose run --rm faust faust -A faust_demo.app worker -l info

