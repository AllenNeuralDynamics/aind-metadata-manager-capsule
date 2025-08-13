# hash:sha256:f76f11307603600de16fae40c621808702afb982fba27807fa50401f14c5c003
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:24.5.0-0-python3.12.4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive

ARG GIT_ASKPASS
ARG GIT_ACCESS_TOKEN
COPY git-askpass /

RUN pip install -U --no-cache-dir \
    -e git+https://github.com/AllenNeuralDynamics/aind-metadata-manager@f519434a0e76581b0ab67bb555115c838b918857#egg=aind-metadata-manager
