# syntax=docker/dockerfile:1
# Illustrative Linux/amd64 image. The base manifest-list digest was read from
# Docker Hub on 2026-11-07; update it deliberately after reviewing a new base.
FROM --platform=linux/amd64 python:3.13.16-slim@sha256:cf50a4f6ac4f026458b08d5222023d700ac806410dff5e9ca8728fa44f2b850f AS builder
WORKDIR /build
COPY requirements-lock-linux-py313.txt ./requirements-lock-linux-py313.txt
RUN python -m pip install --no-cache-dir --prefix=/install -r requirements-lock-linux-py313.txt

FROM --platform=linux/amd64 python:3.13.16-slim@sha256:cf50a4f6ac4f026458b08d5222023d700ac806410dff5e9ca8728fa44f2b850f AS runtime
ARG SOURCE_COMMIT=unknown
ARG SOURCE_WORKTREE_CLEAN=unknown
ARG SOURCE_STATUS_SHA256=unknown
ARG SOURCE_TRACKED_DIFF_SHA256=unknown
ARG SOURCE_UNTRACKED_PATH_COUNT=unknown
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TMPDIR=/run/tmp \
    SOURCE_COMMIT=${SOURCE_COMMIT} \
    SOURCE_WORKTREE_CLEAN=${SOURCE_WORKTREE_CLEAN} \
    SOURCE_STATUS_SHA256=${SOURCE_STATUS_SHA256} \
    SOURCE_TRACKED_DIFF_SHA256=${SOURCE_TRACKED_DIFF_SHA256} \
    SOURCE_UNTRACKED_PATH_COUNT=${SOURCE_UNTRACKED_PATH_COUNT}
RUN groupadd --gid 10001 app \
    && useradd --uid 10001 --gid app --create-home --no-log-init app \
    && mkdir -p /run/tmp \
    && chown -R 10001:10001 /run
WORKDIR /app
COPY --from=builder /install /usr/local
COPY experiment_ops.py sample_experiment.json fixture_manifest.json requirements-lock-linux-py313.txt ./
USER 10001:10001
ENTRYPOINT ["python", "experiment_ops.py"]
CMD ["--backend", "manifest", "--output", "/run/output"]
