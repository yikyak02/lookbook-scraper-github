FROM python:3.11-slim

# Install necessary packages
RUN apt-get update && \
    apt-get install -y \
    wget \
    unzip \
    gnupg \
    curl \
    libgdk-pixbuf2.0-0 \
    libnss3 \
    libatk-bridge2.0-0 \
    libgtk-3-0 && \
    # Install Chromium
    wget -q -O /tmp/chromium.deb https://dl.google.com/linux/direct/chromium-stable_current_amd64.deb && \
    dpkg -i /tmp/chromium.deb || true && \
    apt-get -f install -y && \
    # Install ChromeDriver
    CHROMEDRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget -q "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip" && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -f chromedriver_linux64.zip /tmp/chromium.deb

# Your additional setup commands



# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy the requirements file and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Command to run the application
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]

