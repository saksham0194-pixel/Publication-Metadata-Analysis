# Use the official Python image
FROM python:3.12-slim

# Create a folder for our app
WORKDIR /app

# Copy your code into the container
COPY main.py .

# Install the library your code needs
RUN pip install requests

# Command to run your script
CMD ["python", "main.py"]