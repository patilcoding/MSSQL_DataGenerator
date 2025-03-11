# Use an official Python image as a base
FROM python:3.9

# Set environment variables to accept MSFT EULA and disable interactive mode
ENV ACCEPT_EULA=Y
ENV DEBIAN_FRONTEND=noninteractive

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose any necessary ports (optional, e.g., if running a server)
EXPOSE 8080

# Command to run the application
CMD ["python", "server.py"]
