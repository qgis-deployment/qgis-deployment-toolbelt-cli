# syntax=docker/dockerfile:1
FROM python:3.13-slim

# OCI image specification annotations
# See: https://github.com/opencontainers/image-spec/blob/main/annotations.md
LABEL org.opencontainers.image.authors="Julien Moura (Oslandia) <qgis+qdt@oslandia.com>" \
      org.opencontainers.image.documentation="https://qgis-deployment.github.io/qgis-deployment-toolbelt-cli/"

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # Write .pyc files only once. See: https://stackoverflow.com/a/60797635/2556577
    PYTHONDONTWRITEBYTECODE=1 \
    # Make sure that stdout and stderr are not buffered. See: https://stackoverflow.com/a/59812588/2556577
    PYTHONUNBUFFERED=1 \
    # Remove assert statements and any code conditional on __debug__. See: https://docs.python.org/3/using/cmdline.html#cmdoption-O
    PYTHONOPTIMIZE=2 \
    # Set locale
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# Create non-root user
RUN groupadd --gid 1001 qdt-srv \
    && useradd \
        --uid 1001 \
        --gid qdt-srv \
        --shell /bin/bash \
        --create-home \
        --comment "QGIS Deployment Toolbelt service account" \
        qdt-srv

RUN python -m pip install --no-cache-dir -U pip  \
    && python -m pip install --no-cache-dir -U setuptools setuptools-scm wheel

WORKDIR /home/qdt-srv/

COPY . .

RUN --mount=type=bind,source=.git,target=.git \
    python -m pip install --no-cache-dir -e . \
    && rm -rf /root/.cache

# as non-root user to avoid permission issues with mounted volumes
USER qdt-srv

# set entrypoint to the CLI, so that it can be used directly when running the container
ENTRYPOINT ["qdt"]

# default command
CMD ["--help"]
