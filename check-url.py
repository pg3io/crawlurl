#!/usr/bin/python3

import os
import time
import json
from threading import Thread
import queue as queue
import yaml
import requests

filesource = os.environ['LIST']
url_data = []

def main():
    global url_data
    q = queue.Queue()
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

    while 42:
        file = open_file()
        urls = get_url_array(file)
        for url in urls:
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

                try:
                    line['api']
                except:
                    data.append('')
                else:
                    data.append(line['api'])



def get_url_array(file):
    urls = []

    for url in file['website']:
        try:
            url['search']
        except:
            urls.append([url['url'], False])
        else:
            urls.append([url['url'], True])

    return urls


def format_response(url, req, timereq, warning, danger, result, err_message, tags):
    retry = 0
    if req != None and err_message == '':
        timenow = time.strftime("%d/%m/%Y %H:%M:%S")
        retcode = req.status_code
        html = req.text

        try:
            result = html.count(result)
        except:
            result = 0

        if timereq > danger or retry > 0:
            #"danger"
            status_code = 2
            message = "retry_or_%s_second_time_out" % danger
        elif result <= 0:
            #"danger"
            status_code = 2
            message = "no_word_in_page"
        elif timereq > warning:
            #"warning"
            status_code = 1
            message = "%s_second_time_out" % warning
        elif retcode < 200 and retcode > 226:
            status_code = 2
            message = 'return code of url isn\'t 200 : %s' % retcode
        else:
            #"success"
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
            if url[1] == True:
                req = requests.get(url[0], timeout=10.0)
                url_data.append([req, req.elapsed.total_seconds(), '', url[0], ""])
                q.task_done()
            else:
                req = requests.head(url[0], timeout=10.0)
                url_data.append([req, req.elapsed.total_seconds(), '', url[0], ""])
                q.task_done()
        except requests.exceptions.RequestException as e:
            url_data.append([req, req.elapsed.total_seconds(), '', url[0], str(e)])
            q.task_done()





if __name__ == '__main__':
    while True:
        try:
            main()
        except KeyboardInterrupt:
            exit(1)
