# hash:sha256:b58b69cef74cbe87b9148cea5052da4464235f27c41a9692fca03834a3e9406e
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:24.5.0-0-python3.12.4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-askpass /

RUN --mount=type=secret,id=git-access-token \
    GIT_ACCESS_TOKEN="$(cat /run/secrets/git-access-token)" \
    pip install -U --no-cache-dir \
    -e git+https://github.com/AllenNeuralDynamics/aind-metadata-manager#egg=aind-metadata-manager
