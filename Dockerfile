# Use a slim Python image as the base
FROM python:3.11-slim-bullseye

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # Disable poetry virtual environment creation
    POETRY_VIRTUALENVS_CREATE=false \
    # Install to system instead of virtualenv
    POETRY_VIRTUALENVS_IN_PROJECT=false

# Install Poetry
RUN pip install --no-cache-dir poetry

# Set the working directory
WORKDIR /app

# Copy only the necessary files for Poetry
COPY pyproject.toml poetry.lock ./

# Install dependencies using Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-root

# Copy the rest of the application code
COPY . .

# Set the entrypoint command
CMD ["poetry", "run", "python", "-m", "main"]