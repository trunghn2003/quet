 # Use an official Python runtime as a parent image
 FROM python:3.9-slim-buster

 # Set the working directory in the container to /app
 WORKDIR /app

 # Copy the current directory contents into the container at /app
 COPY . /app

 # Install any needed packages specified in requirements.txt
 # If you don't have a requirements.txt, create one using pip freeze > requirements.txt
 RUN pip install flask bs4 requests googletrans

 # Make port 5000 available to the world outside this container
 EXPOSE 5000

 # Run app.py when the container launches
 CMD ["python", "main.py"]
