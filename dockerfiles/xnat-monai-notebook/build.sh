#!/bin/bash
set -e

export $(xargs < ../../.env)

docker build --build-arg JH_VERSION="$JH_VERSION" \
             -t xnat/monai-notebook:0.3.0 \
             -t xnat/monai-notebook:latest \
             .
