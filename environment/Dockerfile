# hash:sha256:498b9908902f68a52027481b7109d9bf5f6ee47a0cd37eb2f7345d4f1e5832e5
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:24.5.0-0-python3.12.4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-ask-pass /

RUN pip install -U --no-cache-dir \
    aind-metadata-manager==0.1.2 \
    auto-app-panel==0.1.3
