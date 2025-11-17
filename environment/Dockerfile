# hash:sha256:214a87094dbde1941e5775d0048f77c279ea3c04479e24e0e8902fbfd5f1d055
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:24.5.0-0-python3.12.4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-askpass /

RUN --mount=type=secret,id=git-access-token \
    GIT_ACCESS_TOKEN="$(cat /run/secrets/git-access-token)" \
    pip install -U --no-cache-dir \
    -e git+https://github.com/AllenNeuralDynamics/aind-metadata-manager.git@d5d8f56cbf480c3eefcf7f63be7ff845f0605ddc#egg=aind-metadata-manager
