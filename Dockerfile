FROM python:3.9-alpine

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY  check-url.py /usr/src/app/main.py
RUN mkdir /sources

COPY sources/list.yml /sources/list.txt
ENV LIST="/sources/list.txt"
VOLUME ["/sources/"]

CMD [ "python3", "-u", "main.py" ]
