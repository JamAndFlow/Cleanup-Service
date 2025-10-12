FROM python:3.13-alpine

# Set working directory
WORKDIR /app

# Install system dependencies (use Alpine package manager)
# 'apk add --no-cache' keeps the image small and matches the alpine base
RUN apk add --no-cache postgresql-client

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

CMD ["python", "cleanup.py"]
