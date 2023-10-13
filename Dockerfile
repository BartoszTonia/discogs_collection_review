FROM selenium/standalone-chrome:latest

USER root
RUN apt-get update && apt-get install python3-distutils -y
RUN apt-get update && apt-get install -y python3 python3-pip

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONUNBUFFERED=1

ENV APP_HOME /app
WORKDIR /$APP_HOME

COPY . $APP_HOME/

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable for Gunicorn to bind
ENV PORT=8000

# Set up requirements and credentials
RUN pip3 install --no-cache-dir -r requirements.txt

# Run Gunicorn when the container launches
CMD ["gunicorn", "index_flask:app", "-w", "4", "-b", "0.0.0.0:8000"]
#CMD python3 drelease.py






#FROM ubuntu:bionic
#RUN apt-get update && apt-get install -y \
#python3 python3-pip \
#fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 \
#libnspr4 libnss3 lsb-release xdg-utils libxss1 libdbus-glib-1-2 \
#curl unzip wget \
#xvfb
#
## Install chromedriver and google-chrome
#RUN wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/118.0.5993.70/linux64/chromedriver-linux64.zip && \
#unzip chromedriver-linux64.zip -d /usr/bin && \
#cp /usr/bin/chromedriver-linux64/chromedriver /usr/bin/ && \
#chmod +x /usr/bin/chromedriver && \
#rm chromedriver-linux64.zip
#
## Add the repositories and install the gpg key
#RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
#  && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
#wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
#apt-get install -y ./google-chrome-stable_current_amd64.deb && \
#apt-get clean && rm -rf /var/lib/apt/lists/*
#
#ENV LANG C.UTF-8
#ENV LC_ALL C.UTF-8
#ENV PYTHONUNBUFFERED=1
#
#ENV APP_HOME /usr/src/app
#WORKDIR /$APP_HOME
#
#COPY . $APP_HOME/
#
#RUN pip3 install -r requirements.txt
#
#CMD python3 dcollection.py
