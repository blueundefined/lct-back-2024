FROM tiangolo/uvicorn-gunicorn-fastapi:latest

WORKDIR /app/

# Install system dependencies
RUN apt-get update && apt-get install -y libgl1-mesa-dev

# Environment variables for Poetry
ENV POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && export PATH="$POETRY_HOME/bin:$PATH" \
    && poetry config virtualenvs.create false \
    && poetry self update

# Ensure PATH is set for subsequent RUN commands
ENV PATH="$POETRY_HOME/bin:$PATH"

# Copy pyproject.toml and poetry.lock files
COPY pyproject.toml poetry.lock* /app/

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false

# Install dependencies
RUN bash -c "if [ \"$INSTALL_DEV\" = true ] ; then poetry install --no-root ; else poetry install --no-root --only main ; fi"

# Copy the rest of the application code
COPY . /app

CMD ["bash", "./entrypoint.sh"]
