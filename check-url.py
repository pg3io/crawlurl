#!/usr/bin/python

import os
from os import environ
import sys
import re
import fileinput
import urllib2
import time
import ssl
import json
from threading import Thread
import Queue

filesource = os.environ['LIST']
if environ.get('THREAD') is not None:
    nbr_thread = os.environ['THREAD']
if environ.get('DELAY') is not None:
    delay = os.environ['DELAY']

url_data = []

def main():
    global url_data
    file = open_file()
    urls = get_url_array(file)
    q = Queue.Queue(maxsize=0)

    if environ.get('THREAD') is not None:
        for i in range(int(nbr_thread)):
            t = Thread(target=checkurl, args=(q,))
            t.daemon = True
            t.start()
    else:
        for i in range(int(2)):
            t = Thread(target=checkurl, args=(q,))
            t.daemon = True
            t.start()

    while True:
        for url in urls:
            q.put(url)
        q.join()

        fill_limit_data(file)
        for data in url_data:
            format_response(data[3], data[0], data[1], data[5], data[6], data[4])

        url_data = []
        if environ.get('DELAY') is not None:
            time.sleep(float(delay))
        else:
            time.sleep(30)


def fill_limit_data(file):
    for line in file:
        split_line = line.split(" ")
        for data in url_data:
            if split_line[0] == data[3]:
                data.append(split_line[1])
                try:
                    split_line[2]
                except:
                    data.append(0.2)
                else:
                    data.append(split_line[2])
                try:
                    split_line[3]
                except:
                    data.append(0.3)
                else:
                    data.append(split_line[3])


def get_url_array(file):
    urls = []

    for line in file:
        urls.append(line.partition(' ')[0])

    return urls


def format_response(url, req, timereq, warning, danger, result):
    retry = 0
    if req != None:
        timenow = time.strftime("%d/%m/%Y %H:%M:%S")
        retcode = req.getcode()
        html = req.read()
        result = html.count(result)
        if timereq > danger or retry > 0:
            etat = "danger"
            status_code = 2
            message = "retry_or_%s_second_time_out" % danger
        elif result <= 0:
            etat = "danger"
            status_code = 2
            message = "no_word_in_page"
        elif timereq > warning:
            etat = "warning"
            status_code = 1
            message = "%s_second_time_out" % warning
        else:
            etat = "success"
            status_code = 0
            message = "ok"
    else:
        etat = "danger"
        status_code = 2
        message = "ERROR"
        retcode = "000"
        timereq = float(0.00)
        result = "0"
    format_to_json(status_code, etat, timereq, url, retcode, result, message)
    temp.close()


def open_file():
    global temp
    temp = open("%s" % filesource ,"r")
    file = temp.read().splitlines()
    temp.close()

    return file


def format_to_json(status_code, etat, timereq, url, retcode, result, message):
    data = {}

    data['status_code'] = status_code
    data['timereq'] = timereq
    data['url'] = url
    data['retcode'] = retcode
    data['message'] = message
    data_json = json.dumps(data)

    print(data_json)


def checkurl(q):

    while True:
        url = q.get()
        try:
            start = time.time()
            req = urllib2.urlopen(url, timeout = 1)
            end = time.time()
            timereq = end - start

            url_data.append([req, timereq, end, url])
            q.task_done()
        except urllib2.HTTPError, e:
            end = time.time()
            timereq = end - start

            url_data.append([e, timereq, end, url])
            q.task_done()
            return None, None, end
        except urllib2.URLError, e:
            end = time.time()
            timereq = end - start

            url_data.append([e, timereq, end, url])
            q.task_done()
            return None, None, end
        except ssl.SSLError, e:
            end = time.time()
            timereq = end - start

            url_data.append([e, timereq, end, url])
            q.task_done()
            return None, None, end





if __name__ == '__main__':
    while True:
        try:
            main()
        except KeyboardInterrupt:
            exit(1)
