# start by pulling the python image
FROM python:3.10

# copy the requirements file into the image
COPY ./requirements.txt /requirements.txt
COPY ./app.py /app.py

# switch working directory
WORKDIR /

# install the dependencies and packages in the requirements file
RUN pip3 install -r requirements.txt

# copy every content from the local file to the image
COPY ./application /application

# configure the container to run in an executed manner
EXPOSE 5000
