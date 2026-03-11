# hash:sha256:df27af11b5223fa1abdbddcc684a4824055bdb621895fe9389d23e63183dce1b
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:24.5.0-0-python3.12.4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-ask-pass /

RUN pip install -U --no-cache-dir \
    aind-metadata-manager==0.1.1
