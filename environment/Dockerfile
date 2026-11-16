# hash:sha256:f7e8ba31cc963439c255b208ca765f571de600c213728d14955cbf51ded03aab
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:24.5.0-0-python3.12.4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-ask-pass /

RUN --mount=type=secret,id=git-access-token \
    GIT_ACCESS_TOKEN="$(cat /run/secrets/git-access-token)" \
    pip install -U --no-cache-dir \
    log-schema==0.2.10.dev1 \
    -e git+https://github.com/AllenNeuralDynamics/aind-metadata-manager.git@v0.3.3#egg=aind-metadata-manager
