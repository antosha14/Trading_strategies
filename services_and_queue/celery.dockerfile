FROM python:3.12

WORKDIR /app/

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./data_filler/pyproject.toml ./data_filler/poetry.lock* /app/

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --only main ; fi"

ENV C_FORCE_ROOT=1

ENV PYTHONPATH=/app

COPY ./services_and_queue/worker-start.sh /worker-start.sh

COPY ./data_filler/app /app/app
COPY ./services_and_queue /app/services_and_queue

RUN chmod +x /worker-start.sh

CMD ["bash", "/worker-start.sh"]