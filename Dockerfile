# set base image (host OS)
FROM python:3.10

# set the working directory in the container
WORKDIR /code

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y \
    imagemagick ffmpeg

COPY src/ .

# command to run on container start
CMD [ "gunicorn", "main:app" ]
