# set base image (host OS)
FROM python:3.8

# set the working directory in the container
WORKDIR .

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt
RUN apt install ffmpeg imagemagick

# command to run on container start
CMD [ "gunicorn", "main:app" ]
