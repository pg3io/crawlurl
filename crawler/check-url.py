#!/usr/bin/python
import os
import time
import json
import re
from threading import Thread
import queue
import yaml
import requests
from datetime import datetime
import urllib3.request as req3

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

try:
    filesource = os.environ['LIST']
except KeyError:
    print('Error: LIST environnement variable is mandatory.')
    exit(1)
url_data = []

def main():
    db_con = False
    global url_data
    q = queue.Queue()
    file = open_file()
    write_api = connect_to_influxdb()

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
            db_con = format_response(write_api, db_con, data[3], data[0], data[1], data[6], data[7], data[5], data[4], data[8])
        url_data.clear()
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


def format_response(write_api, db_con, url, req, timereq, warning, danger, result, err_message, tags):
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
    return (format_to_json(write_api, db_con, status_code, timereq, url, retcode, message, tags))


def open_file():
    with open(filesource, 'r') as stream:
        try:
            file = yaml.load(stream, Loader=yaml.FullLoader)
        except yaml.YAMLError as exc:
            print(exc)

    return file


def insert_to_influxdb(write_api, db_con, data_json):
    flag = False
    array = [
        data_json["url"],
        data_json["status_code"],
        data_json["timereq"],
        data_json["retcode"],
        data_json["message"]
    ]
    try:
        array.append(data_json["tags"])
    except KeyError:
        pass
    else:
        flag = True
    sequence = [
        f'server_response,host={array[0]} status_code={array[1]},timereq={array[2]},retcode={array[3]},message="{array[4]}"'
    ]
    if flag:
        sequence.append(f'tags,host={array[0]} tags="{array[5]}"')
    while True:
        try:
            write_api.write(os.environ['INFLUXDB-BUCKET'], os.environ['INFLUXDB-ORG'], sequence)
        except Exception as e:
            print('Waiting 10 seconds for InfluxDB to start...')
            print('Script is unable to connect :\n', str(e))
            time.sleep(10)
        else:
            if not db_con:
                print('Connected to  InfluxDB !')
            break
    return True


def format_to_json(write_api, db_con, status_code, timereq, url, retcode, message, tags):
    data = {}

    data['status_code'] = status_code
    data['timereq'] = timereq
    data['url'] = url
    data['retcode'] = retcode
    data['message'] = message
    if tags != '':
        data['tags'] = tags
    data_json = json.dumps(data)
    if write_api != None:
        insert_to_influxdb(write_api, db_con, data)
        return True
    else:
        print(data_json)
        return False


def checkurl(q):
    flag = False
    while True:
        url = q.get()
        if flag:
            url[0] = re.sub(r"\/[a-z0-9].", '/', url[0])
        try:
            if url[1] == True:
                req = requests.get(url[0], timeout=10.0)
                url_data.append([req, req.elapsed.total_seconds(), '', url[0], ""])
                q.task_done()
            else:
                req = requests.head(url[0], timeout=10.0)
                url_data.append([req, req.elapsed.total_seconds(), '', url[0], ""])
                q.task_done()
        except Exception as e:
            if e == requests.ReadTimeout:
                flag = True
            else:
                print(e)


def connect_to_influxdb():
    try:
        influxdb_host = os.environ['INFLUXDB-HOST']
    except:
        print('INFLUXDB-HOST environnement variable is not set, running without InfluxDB')
        return None
    else:
        if (influxdb_host != None and influxdb_host != ''):
            try:
                os.environ['INFLUXDB-TOKEN']
                os.environ['INFLUXDB-ORG']
                os.environ['INFLUXDB-BUCKET']
            except:
                print('INFLUXDB-HOST is defined please define INFLUX-TOKEN, INFLUX-ORG and INFLUX-BUCKET environnement variables.')
                exit(1)
        else:
            print('INFLUXDB-HOST environnement variable is empty, running without InfluxDB')
            return None       
        if (influxdb_host != None and influxdb_host != ''):
            client = InfluxDBClient(url=influxdb_host, token=os.environ['INFLUXDB-TOKEN'])
            return client.write_api(write_options=SYNCHRONOUS)
        
    

if __name__ == '__main__':
    while True:
        try:
            main()
        except KeyboardInterrupt:
            exit(1)
