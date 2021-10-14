FROM python:3.10-slim as compile-image
RUN apt-get update
RUN apt-get install -y --no-install-recommends gcc build-essential && rm -rf /var/lib/apt/lists/*

RUN mkdir -m 777 /app
COPY pyproject.toml poetry.lock /app/
WORKDIR /app

RUN python -m venv .venv && .venv/bin/pip install --upgrade pip
RUN .venv/bin/pip install poetry
RUN .venv/bin/poetry update
RUN .venv/bin/poetry install --no-root --no-dev

##############################################################

FROM python:3.10-slim AS runtime-image
RUN groupadd --gid 2000 py && useradd --uid 2000 --gid py --shell /bin/bash --create-home py


COPY --from=compile-image --chown=py:py /app /app
COPY --from=compile-image --chown=py:py /app/.venv /app/

RUN mkdir -m 777 /app/jokes/
COPY --chown=py:py *.py /app/
COPY  --chown=py:py jokes/*.json /app/jokes/

USER py

WORKDIR /app
ENTRYPOINT ["/app/.venv/bin/python3"]
CMD ["index.py"]
