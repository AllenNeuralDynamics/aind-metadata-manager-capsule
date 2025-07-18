# hash:sha256:1f38c4a59ed81fd13ae54269889a9fc640ecec6383665871c7810643531a0ad5
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/jupyterlab:3.0.9-miniconda4.9.2-python3.8-ubuntu20.04

ARG DEBIAN_FRONTEND=noninteractive

ARG GIT_ASKPASS
ARG GIT_ACCESS_TOKEN
COPY git-askpass /

RUN pip3 install -U --no-cache-dir \
    aind-data-schema==1.2.0 \
    aind-data-schema-models \
    aind-metadata-upgrader==0.0.24 \
    pydantic \
    pydantic-settings
