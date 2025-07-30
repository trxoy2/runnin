FROM python:3.9-slim

# Set environment variables to prevent Python from writing .pyc files and buffering output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# create the last_run.txt file if it doesn't exist
RUN mkdir -p /app/data && touch /app/data/last_run.txt

# Set the working directory
WORKDIR /app

# Copy the requirements file separately for better caching
COPY requirements.txt .

# Install the dependencies
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Make the script executable
RUN chmod +x run.sh

# Run the ETL pipeline script
CMD ["./run.sh"]