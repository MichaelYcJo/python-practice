# pull official base image
FROM python:3.7-alpine

RUN apk update && \
    apk add python3 python3-dev \
            gcc musl-dev linux-headers zlib zlib-dev \
            freetype freetype-dev jpeg jpeg-dev libffi-dev \
            postgresql-dev

# set work directory
WORKDIR /usr/src/app

# copy project
COPY . /usr/src/app/

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# run development server
CMD /usr/local/bin/gunicorn config.wsgi:application -w 2 -b :$PORT