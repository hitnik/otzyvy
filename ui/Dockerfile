FROM node:15.4-alpine

ADD https://api.github.com/repos/hitnik/forums_ui/git/refs/heads/master version.json

# set work directory
RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

#install git
RUN apk update && apk add git

#clone project from git
RUN git clone -b master https://github.com/hitnik/forums_ui.git .
RUN git checkout master

# copy entrypoint.sh
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

# Build args
ENV API_HOST=$API_HOST
ENV PRODUCTION TRUE


#install node dependencies
RUN npm install
RUN npm fund

#install HTTp server
RUN npm install --global http-server