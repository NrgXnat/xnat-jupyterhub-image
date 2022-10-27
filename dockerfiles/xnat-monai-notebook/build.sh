#!/bin/bash
set -e

export $(xargs < ../../.env)

docker build --build-arg JH_VERSION="$JH_VERSION"\
             -t xnat/monai-notebook:latest \
             -t xnat/monai-notebook:0.2.0 \
             .
