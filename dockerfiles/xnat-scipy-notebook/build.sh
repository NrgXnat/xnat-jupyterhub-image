#!/bin/bash
set -e

export $(xargs < ../../.env)

docker build --build-arg JH_VERSION="$JH_VERSION"\
             -t xnat/scipy-notebook:latest \
             -t xnat/scipy-notebook:0.3.0-beta1 \
             .
