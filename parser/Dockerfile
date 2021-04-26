# pull official base image
FROM hitnik/python3.8-alpine-pgsql:0.1

#set work directory
WORKDIR /usr/src/app

# copy project
COPY . .

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
RUN \
 python3 -m pip install -r requirements.txt --no-cache-dir && \
 apk --purge del .build-deps
