FROM python

# Set the working directory in the container
WORKDIR /app
# Установка Poetry
RUN pip install poetry

# Copy the requirements files to the container
COPY pyproject.toml poetry.lock ./

# Install Poetry and dependencies
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

COPY . .

# Define the command to run your application
CMD ["python", "main.py"]