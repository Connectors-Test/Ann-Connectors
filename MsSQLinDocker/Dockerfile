FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

# System dependencies for pyodbc + MSSQL
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    gnupg \
    unixodbc \
    unixodbc-dev \
    libpq-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Microsoft ODBC Driver 18 for SQL Server
RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg && \
    install -o root -g root -m 644 microsoft.gpg /etc/apt/trusted.gpg.d/ && \
    rm microsoft.gpg && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Set working directory
WORKDIR /app

# Copy code
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r app/requirements.txt

# Expose port
EXPOSE 5000

# Run app
CMD ["python", "main.py"]