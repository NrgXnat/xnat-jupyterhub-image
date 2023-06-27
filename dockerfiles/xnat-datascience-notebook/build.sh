#!/bin/bash
set -e

export $(xargs < ../../.env)

docker build --build-arg JH_VERSION="$JH_VERSION"\
             -t xnat/datascience-notebook:latest \
             -t xnat/datascience-notebook:1.0.0-RC2 \
             .