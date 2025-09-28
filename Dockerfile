# Dockerfile
# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on (Cloud Run defaults to $PORT, but 8080 is a common standard)
ENV PORT 8080
EXPOSE 8080

# Run the application using Uvicorn. The 'api_main:app' assumes your FastAPI app is named 'app' in 'api_main.py'
CMD ["uvicorn", "api_main:app", "--host", "0.0.0.0", "--port", "8080"]
