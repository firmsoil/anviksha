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

# Expose the port the app runs on (standardizing on 8080)
ENV PORT 8080
EXPOSE 8080

# Run the application using Uvicorn, pointing to the 'app' object 
# inside the 'api_main.py' module of the 'cicd_api' package.
CMD ["uvicorn", "cicd_api.api_main:app", "--host", "0.0.0.0", "--port", "8080"]
