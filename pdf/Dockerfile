# pull official base image
FROM surnet/alpine-python-wkhtmltopdf:3.7.3-0.12.5-small

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

#set work directory
WORKDIR /usr/src/app

# copy entrypoint.sh
#COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

# copy project
COPY . .

# install dependencies
RUN pip install --upgrade pip
RUN python3 -m pip install -r requirements.txt --no-cache-dir