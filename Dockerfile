FROM python:2-alpine

ENV LIST="/sources/list.txt"
COPY  check-url.py /usr/src/app/main.py
RUN mkdir /sources && touch /sources/list.txt

WORKDIR /usr/src/app
VOLUME ['/sources/']

CMD [ "python", "-u", "main.py" ]
