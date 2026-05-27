# qMax <qwiglydee@gmail.com>
#
# Building backend from ./back -> /app/
# Building frontend from ./front -> /app/static/
#

#### base
# - creating non-root app user
FROM python:3.11-slim AS base

# creating non-root user
# Note: for bind mounts to work, the IDs should match local user
ARG USERUID=1000
ARG USERGID=1000
RUN addgroup --system --gid=$USERGID appgroup && adduser --system --uid=$USERUID --ingroup appgroup --home /app --shell /bin/sh --disabled-password appuser
RUN chown appuser:appgroup /app

# RUN apt-get update

#### buildpy
# - installing/building python requirements
FROM base AS buildpy

# #some requirements w/out wheels might need building
# RUN apt-get -y install --no-install-recommends \
#     build-essential \
#     python3-dev

USER appuser:appgroup
WORKDIR /app

COPY requirements.* /app/

# installs everything into /app/.local/lib
RUN pip install --user -r requirements.txt

#### prod
# - copying everything into single image
FROM base AS prod
####
USER appuser:appgroup
WORKDIR /app

COPY . /app/
COPY --from=buildpy /app/.local/ /app/.local/
# COPY --from=buildjs /app/dist/ /app/static/

# ENV PATH=/app/.venv/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

CMD ["python", "run.py"]
