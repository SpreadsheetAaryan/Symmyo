# Use a Python base image suitable for data science libraries (slim is smaller)
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy the requirements file and install dependencies
# This caches the dependency layer if requirements.txt doesn't change
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application source code
COPY . .

# Expose the port Flask will run on
EXPOSE 5000

# Command to run the Flask application when the container starts
# We use 'flask run' in debug mode for development
CMD ["python", "app/app.py"]