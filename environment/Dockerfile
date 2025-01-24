# hash:sha256:fe0098ec5af7a32f327388adf791a999896e70e7472f0308c22a0e63a6f3e522
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/jupyterlab:3.0.9-miniconda4.9.2-python3.8-ubuntu20.04

ARG DEBIAN_FRONTEND=noninteractive

ARG GIT_ASKPASS
ARG GIT_ACCESS_TOKEN
COPY git-askpass /

RUN pip3 install -U --no-cache-dir \
    aind-data-schema==1.2.0 \
    aind-metadata-upgrader==0.0.24
