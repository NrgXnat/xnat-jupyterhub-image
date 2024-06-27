#!/bin/bash
set -e

export $(xargs < ../../.env)

docker build --no-cache --build-arg JH_VERSION="$JH_VERSION"\
             -t xnat/datascience-notebook:1.2.0 \
             -t xnat/datascience-notebook:latest \
             .