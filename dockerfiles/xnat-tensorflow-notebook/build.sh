#!/bin/bash
set -e

export $(xargs < ../../.env)

docker build --build-arg JH_VERSION="$JH_VERSION"\
             -t xnat/tensorflow-notebook:latest \
             -t xnat/tensorflow-notebook:0.2.0 \
             .
