FROM python:2.7.15-alpine

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY  check-url.py /usr/src/app/main.py
RUN mkdir /sources && touch /sources/list.txt

ENV LIST="/sources/list.txt"
VOLUME ['/sources/']

CMD [ "python2", "-u", "main.py" ]
