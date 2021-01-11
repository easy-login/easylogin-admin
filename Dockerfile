# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install binary libraties
RUN apt-get -y update
RUN apt-get -y install gcc python3-dev libssl-dev default-libmysqlclient-dev
RUN mkdir -p /var/log/sociallogin

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Initialization
RUN DEBUG=1 python manage.py collectstatic --no-input

# Run wsgi.py when the container launches
CMD ["./bin/docker-server"]
