# hash:sha256:dc3f0813a3ecf39f36119571f229b838bb160acef199f90e5f35c10a8a7c9698
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:24.5.0-0-python3.12.4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-ask-pass /

RUN --mount=type=secret,id=git-access-token \
    GIT_ACCESS_TOKEN="$(cat /run/secrets/git-access-token)" \
    pip install -U --no-cache-dir \
    -e git+https://github.com/AllenNeuralDynamics/aind-metadata-manager.git@a891e2c#egg=aind-metadata-manager
