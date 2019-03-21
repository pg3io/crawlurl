#!/usr/bin/python

import os
import urllib2
import time
import ssl
import json
from threading import Thread
import Queue
import yaml
import certifi

filesource = os.environ['LIST']
url_data = []

def main():
    global url_data
    q = Queue.Queue(maxsize=0)
    file = open_file()

    try:
        file['thread']
    except:
        for i in range(int(1)):
            t = Thread(target=checkurl, args=(q,))
            t.daemon = True
            t.start()
    else:
        for i in range(int(file['thread'])):
            t = Thread(target=checkurl, args=(q,))
            t.daemon = True
            t.start()

    while True:
        file = open_file()
        urls = get_url_array(file)
        for url in urls:
            if url[0] != "#":
                q.put(url)
        q.join()

        fill_limit_data(file)
        for data in url_data:
            format_response(data[3], data[0], data[1], data[6], data[7], data[5], data[4], data[8])

        url_data = []

        try:
            file['delay']
        except:
            time.sleep(30)
        else:
            time.sleep(float(file['delay']))


def fill_limit_data(file):
    for line in file['website']:
        for data in url_data:
            if line['url'] == data[3]:
                try:
                    line['search']
                except:
                    data.append('')
                else:
                    data.append(line['search'])

                try:
                    line['warning']
                except:
                    data.append(0.2)
                else:
                    data.append(line['warning'])

                try:
                    line['critical']
                except:
                    data.append(0.3)
                else:
                    data.append(line['critical'])

                try:
                    line['tags']
                except:
                    data.append('')
                else:
                    data.append(line['tags'])



def get_url_array(file):
    urls = []

    for url in file['website']:
        urls.append(url['url'])

    return urls


def format_response(url, req, timereq, warning, danger, result, err_message, tags):
    retry = 0
    if req != None:
        timenow = time.strftime("%d/%m/%Y %H:%M:%S")
        retcode = req.getcode()
        html = req.read()

        try:
            result = html.count(result)
        except:
            result = 0

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
        status_code = 2
        message = err_message
        retcode = "000"
        timereq = float(0.00)
    format_to_json(status_code, timereq, url, retcode, message, tags)


def open_file():
    with open(filesource, 'r') as stream:
        try:
            file = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    return file


def format_to_json(status_code, timereq, url, retcode, message, tags):
    data = {}

    data['status_code'] = status_code
    data['timereq'] = timereq
    data['url'] = url
    data['retcode'] = retcode
    data['message'] = message
    if tags != '':
        data['tags'] = tags
    data_json = json.dumps(data)

    print(data_json)


def checkurl(q):
    while(True):
        url = q.get()
        try:
            start = time.time()
            req = urllib2.urlopen(url, timeout = 2, cafile=certifi.where())
            end = time.time()
            timereq = end - start
            url_data.append([req, timereq, end, url, ""])
            q.task_done()
        except urllib2.HTTPError, e:
            end = time.time()
            timereq = end - start

            url_data.append([req, timereq, end, url, "HTTP_ERROR"])
            q.task_done()
        except urllib2.URLError, e:
            end = time.time()
            timereq = end - start

            url_data.append([None, timereq, end, url, "URL_ERROR"])
            q.task_done()
        except ssl.SSLError, e:
            end = time.time()
            timereq = end - start

            url_data.append([None, timereq, end, url, "SSL_ERROR"])
            q.task_done()





if __name__ == '__main__':
    while True:
        try:
            main()
        except KeyboardInterrupt:
            exit(1)
