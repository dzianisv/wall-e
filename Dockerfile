# Use the official Python image from the Alpine variant
FROM python:3.12-alpine

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apk add --no-cache \
    build-base \
    libffi-dev \
    openssl-dev \
    cargo \
    git

# Install pipenv
RUN pip install --upgrade pip && \
    pip install pipenv

# Set the working directory
WORKDIR /app

# Copy Pipfile and Pipfile.lock to the working directory
COPY Pipfile Pipfile.lock /app/

# Install Python dependencies
RUN pipenv install --deploy --ignore-pipfile

# Copy the rest of the application code
COPY . /app

# Command to run the application
CMD ["pipenv", "run", "python", "src/bot.py"]