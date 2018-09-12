# Use an official Python runtime as a parent image
FROM python:3.7-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install binary libraties
RUN apt -y update
RUN apt -y install gcc python3-dev libssl-dev mysql-client libmariadbclient-dev
RUN mkdir -p /var/log/sociallogin

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 8081 available to the world outside this container
EXPOSE 8081

# Define environment variable
ENV DEBUG True

# Run wsgi.py when the container launches
CMD ["sh", "runserver.sh"]