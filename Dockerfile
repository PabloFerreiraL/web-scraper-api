FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ /app/

# Set environment variables
ENV FLASK_APP=app.main
ENV FLASK_ENV=development

# Expose port
EXPOSE 5000

# Run the application
#CMD ["python", "main.py"]
CMD ["flask", "run", "--host=0.0.0.0"]