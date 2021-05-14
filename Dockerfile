FROM python:3.9-slim as compile-image
RUN apt-get update
RUN apt-get install -y --no-install-recommends gcc build-essential

RUN rm -rf /var/lib/apt/lists/*

RUN mkdir -m 777 /app
COPY pyproject.toml poetry.lock /app/
WORKDIR /app

RUN python -m venv .venv && .venv/bin/pip install --upgrade pip
RUN .venv/bin/pip install poetry
RUN .venv/bin/poetry update
RUN .venv/bin/poetry install --no-root --no-dev

##############################################################

FROM python:3.9-slim AS runtime-image

COPY --from=compile-image /app /app
COPY --from=compile-image /app/.venv /app/

RUN mkdir /app/jokes/
COPY *.py /app/
COPY jokes/*.json /app/jokes/

WORKDIR /app
ENTRYPOINT ["/app/.venv/bin/python3"]
CMD ["index.py"]
