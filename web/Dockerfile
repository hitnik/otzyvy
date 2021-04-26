# pull official base image
FROM hitnik/python3.8-alpine-pgsql:0.1

#set work directory
WORKDIR /usr/src/app

# copy project
COPY . .

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN python3 -m pip install -r requirements.txt --no-cache-dir
RUN apk --purge del .build-deps
#make stsic dir
RUN mkdir -p ./static
