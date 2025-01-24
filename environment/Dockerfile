# hash:sha256:096bba637db91b1bfd99eee6d05dc1153a141beefc73dbc1ae13f1b709bcd3ea
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/jupyterlab:3.0.9-miniconda4.9.2-python3.8-ubuntu20.04

ARG DEBIAN_FRONTEND=noninteractive

ARG GIT_ASKPASS
ARG GIT_ACCESS_TOKEN
COPY git-askpass /

RUN pip3 install -U --no-cache-dir \
    aind-data-schema==1.2.0 \
    aind-metadata-upgrader
