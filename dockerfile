FROM python:3.9

# instal ssh client

RUN apt-get update && apt-get install -y openssh-client


# set envirement variables

ENV PYTHONUNBUFFERED 1

# Set the working directory

WORKDIR /app

# Copy the requirements.txt file

COPY requirements.txt /app/requirements.txt

# install python dependencies
RUN pip install -r requirements.txt


#copy the application to the working directory

COPY . /app

# Start the ssh tunnel
CMD python manage.py runserver 0.0.0.0:8000