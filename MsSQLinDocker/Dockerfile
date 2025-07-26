FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install Microsoft ODBC Driver 18 and mssql-tools
RUN apt-get update && apt-get install -y \
    curl gnupg apt-transport-https software-properties-common python3 python3-pip\
    && curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/trusted.gpg.d/microsoft.gpg \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update && ACCEPT_EULA=Y apt-get install -y \
    msodbcsql18 mssql-tools18 unixodbc-dev \
    && echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc \
    && export PATH="$PATH:/opt/mssql-tools18/bin"

# Set working directory
WORKDIR /app

# Copy code
COPY app/ .

# Install Python deps
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 5000

CMD ["python3", "main.py"]