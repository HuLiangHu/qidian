FROM python:2.7
MAINTAINER Madison Bahmer <jally@outlook.com>

# os setup
RUN apt-get update && apt-get -y install \
  python-lxml \
  build-essential \
  libssl-dev \
  libffi-dev \
  python-dev \
  libxml2-dev \
  libxslt1-dev \
  && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# install requirements
COPY . /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt


# override settings via localsettings.py
COPY settings.py /usr/src/app/crawling/localsettings.py
# set up environment variables

# run the spider
ENTRYPOINT ["scrapy", "runspider"]