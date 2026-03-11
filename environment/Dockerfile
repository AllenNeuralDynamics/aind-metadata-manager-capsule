# hash:sha256:015cddb131a915f8667245a5eabd6416d208be79297d8e1b581be92a282f1a8a
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:24.5.0-0-python3.12.4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-ask-pass /

RUN pip install -U --no-cache-dir \
    aind-metadata-manager==0.1.2
