FROM ubuntu:bionic
RUN apt-get update && apt-get install -y \
python3 python3-pip \
fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 \
libnspr4 libnss3 lsb-release xdg-utils libxss1 libdbus-glib-1-2 \
curl unzip wget \
xvfb

# Install geckodriver and firefox
# ...

# Install chromedriver and google-chrome
RUN wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/118.0.5993.70/linux64/chromedriver-linux64.zip && \
unzip chromedriver-linux64.zip -d /usr/bin && \
cp /usr/bin/chromedriver-linux64/chromedriver /usr/bin/ && \
chmod +x /usr/bin/chromedriver && \
rm chromedriver-linux64.zip

# Add the repositories and install the gpg key
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
  && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list

RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
# Install Chrome with apt-get to automatically handle dependencies

RUN apt-get install -y ./google-chrome-stable_current_amd64.deb

RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
# apt-get install -y ./google-chrome-stable_current_amd64.deb && \
# apt-get clean && rm -rf /var/lib/apt/lists/* && \
# rm ./google-chrome-stable_current_amd64.deb


ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONUNBUFFERED=1
ENV PATH="${PATH}:/usr/bin/chromedriver-linux64"

ENV APP_HOME /usr/src/app
WORKDIR /$APP_HOME

COPY . $APP_HOME/

RUN pip3 install -r requirements.txt

CMD python3 dcollection.py
