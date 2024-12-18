# Use an official Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .
COPY credentials.json /app/credentials.json


# Expose the port Flask will run on
EXPOSE 8080

# Start the Flask application
CMD ["python", "app.py"]
