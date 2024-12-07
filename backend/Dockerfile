FROM python:3-slim
EXPOSE 8000
WORKDIR /opt/cloud_store

# Install system dependencies
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements/base.txt requirements/base.txt
COPY requirements/staging.txt requirements/staging.txt
RUN pip install -r requirements/staging.txt

# Copy project files
COPY . .

# Run migrations and start app
CMD ["sh", "-c", "flask db upgrade && gunicorn --bind 0.0.0.0:8000 'run:create_app()'"]
