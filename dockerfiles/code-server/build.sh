#!/bin/bash
set -e

export $(xargs < ../../.env)

docker build --build-arg JH_VERSION="$JH_VERSION" \
             -t awlassit/datascience-code-server:0.0.1 \
             .
