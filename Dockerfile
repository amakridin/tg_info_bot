FROM python:3.9 as requirements-builder

RUN mkdir build/
WORKDIR /build/

RUN pip install poetry

COPY pyproject.toml poetry.lock /build/

RUN poetry export --with-credentials --without-hashes -f requirements.txt -o requirements.txt

FROM python:3.9

RUN mkdir app/
WORKDIR /app/

COPY --from=requirements-builder /build/requirements.txt /app/requirements.txt

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100

RUN pip install -r requirements.txt

COPY common_tg_bot /app/tg_simple_math_bot


CMD ["python", "-m", "tg_simple_math_bot.app"]