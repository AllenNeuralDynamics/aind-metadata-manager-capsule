# hash:sha256:f7bccbc39124352bf68d507d1d845c7021eaf578b666aee3696fe3efc181fabc
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:24.5.0-0-python3.12.4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-ask-pass /

RUN --mount=type=secret,id=git-access-token \
    GIT_ACCESS_TOKEN="$(cat /run/secrets/git-access-token)" \
    pip install -U --no-cache-dir \
    -e git+https://github.com/AllenNeuralDynamics/aind-metadata-manager.git@v0.3.1#egg=aind-metadata-manager
