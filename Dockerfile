FROM python:3.12

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && apt-get clean

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Ensure Poetry is in PATH
ENV PATH="/root/.local/bin:$PATH"

# Set work directory
RUN mkdir -p /code
WORKDIR /code

# Copy project files
COPY pyproject.toml poetry.lock /code/

# Configure Poetry to not create virtual environments
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --only main --no-root --no-interaction

# Copy the rest of the code
COPY . /code

# Run the application
CMD ["poetry", "run", "python", "main.py"]
