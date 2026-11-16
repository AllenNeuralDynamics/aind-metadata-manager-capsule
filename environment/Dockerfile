# hash:sha256:b1522223233a50fcce5d8b649451b4ecc3b8a173c4d6dc0363296fa537eeb6c5
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:24.5.0-0-python3.12.4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-ask-pass /

RUN --mount=type=secret,id=git-access-token \
    GIT_ACCESS_TOKEN="$(cat /run/secrets/git-access-token)" \
    pip install -U --no-cache-dir \
    log-schema==0.2.10.dev1 \
    watchtower==3.4.0 \
    -e git+https://github.com/AllenNeuralDynamics/aind-metadata-manager.git@v0.3.3#egg=aind-metadata-manager
