FROM python:3.12

WORKDIR /code/

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./data_filler/pyproject.toml ./data_filler/poetry.lock /code/

# Allow installing dev dependencies to run tests

ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --only main ; fi"

ENV PYTHONPATH=/code

COPY ./data_filler/prestart.sh /code/

COPY ./data_filler/app /code/app
COPY ./services_and_queue /code/services_and_queue

EXPOSE 8888

CMD ["fastapi", "run", "./app/main.py", "--proxy-headers", "--port", "8888"]