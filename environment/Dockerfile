# hash:sha256:0013a735c5310f5514ad6197d6e809b78402480393397c176bda71fdc36fab65
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:24.5.0-0-python3.12.4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-askpass /

RUN --mount=type=secret,id=git-access-token \
    GIT_ACCESS_TOKEN="$(cat /run/secrets/git-access-token)" \
    pip install -U --no-cache-dir \
    -e git+https://github.com/AllenNeuralDynamics/aind-metadata-manager@2cea55f4add6678a6a8513f144936d4c44815cc7#egg=aind-metadata-manager
