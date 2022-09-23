#!/bin/bash
set -e

export $(xargs < ../.env)

docker build --build-arg JH_VERSION="$JH_VERSION"\
             -t xnat/jupyterhub-single-user:latest \
             -t xnat/jupyterhub-single-user:0.1.1-SNAPSHOT \
             .
