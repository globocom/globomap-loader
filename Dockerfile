FROM ubuntu:16.04

RUN apt-get update
RUN apt-get install -y software-properties-common vim
RUN add-apt-repository ppa:jonathonf/python-3.6
RUN apt-get update

RUN apt-get install -y python-dev libmysqlclient-dev
RUN apt-get install -y build-essential python-pip
RUN apt-get install -y git

# update pip
RUN python -m pip install pip --upgrade
RUN python -m pip install wheel

ADD . /app

WORKDIR /app

RUN pip install -r requirements_test.txt
