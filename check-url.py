#!/usr/bin/python
import os
import time
from threading import Thread
import queue
import yaml
import requests
import sys
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

try:
    filesource = os.environ['LIST']
except KeyError:
    print('Missing LIST environnement variable, exiting.')
    sys.exit(1)

url_data = []

def main():
    db_con = False
    global url_data
    global config
    q = queue.Queue()
    config = parse_config()
    write_api = connect_to_influxdb()
    if 'thread' in config:
        for i in range(int(config['thread'])):
            t = Thread(target=checkurl, args=(q,))
            t.daemon = True
            t.start()
    else:
        for i in range(int(1)):
            t = Thread(target=checkurl, args=(q,))
            t.daemon = True
            t.start()

    while 42:
        tmp_config = parse_config()
        if config != tmp_config:
            config = tmp_config
            print('config has changed : reloading...')
        urls = get_url_array(config)
        for url in urls:
                q.put(url)
        q.join()

        fill_limit_data(config)
        for data in url_data:
            db_con = format_response(write_api, db_con, data[3], data[0], data[1], data[6], data[7], data[5], data[4], data[8])
        
        url_data.clear()

        if 'delay' in config:
            time.sleep(float(config['delay']))
        else:
            time.sleep(30)


def fill_limit_data(config):
    for site in config['website']:
        for data in url_data:
            if site['url'] == data[3]:
                if 'search' in site:
                    data.append(site['search'])
                else:
                    data.append('')
                
                if 'warning' in site:
                    data.append(site['warning'])
                else:
                    data.append(0.2)
                    
                if 'critical' in site:
                    data.append(site['critical'])
                else:
                    data.append(0.3)

                if 'tags' in site:
                    data.append(site['tags'])
                else:
                    data.append('')

                if 'api' in site:
                    data.append(site['api'])
                else:
                    data.append('')



def get_url_array(config):
    urls = []

    for url in config['website']:
        if 'search' in url:
            urls.append([url['url'], True])
        else:
            urls.append([url['url'], False])

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
        if retcode < 200 or retcode > 226:
            status_code = 2
            message = 'return code of url isn\'t 200 : %s' % retcode
        elif timereq > danger or retry > 0:
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
        else:
            #"success"
            status_code = 0
            message = "ok"
    else:
        print('An exception has been handled during crawling.')
        status_code = 2
        message = err_message
        retcode = "000"
        timereq = float(0.00)
    return (format_to_json(write_api, db_con, status_code, timereq, url, retcode, message, tags))


def parse_config() -> dict:
    config = {}
    with open(filesource, 'r') as stream:
        try:
            config = yaml.load(stream, Loader=yaml.FullLoader)
        except yaml.YAMLError as exc:
            print(exc)
    return config


def insert_to_influxdb(write_api, db_con, data_json):
    sequence = [
        f'''server_response,host={data_json['url']} status_code={data_json['status_code']},timereq={data_json['timereq']},retcode={data_json['retcode']},message="{data_json['message']}",tag="{data_json['tag']}"'''
    ]
    try:
        sequence.append(f'''tags,host={data_json['url']} tags="{data_json['tags']}"''')
    except KeyError:
        pass
    while 42:
        try:
            write_api.write(os.environ['INFLUXDB-BUCKET'], os.environ['INFLUXDB-ORG'], sequence)
        except Exception as e:
            print('Waiting 10 seconds for InfluxDB to start...')
            print('Script is unable to connect :\n', str(e))
            time.sleep(10)
        else:
            if not db_con:
                print('Connected to InfluxDB !')
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
        data['tag'] = tags[0]
    if write_api != None:
        insert_to_influxdb(write_api, db_con, data)
        return True
    else:
        print(data)
        return False


def checkurl(q):
    while True:
        url = q.get()
        try:
            if url[1] == True:
                req = requests.get(url[0], timeout=(10, 30))
                url_data.append([req, req.elapsed.total_seconds(), '', url[0], ""])
                q.task_done()
            else:
                req = requests.head(url[0], timeout=(10, 30))
                url_data.append([req, req.elapsed.total_seconds(), '', url[0], ""])
                q.task_done()
        except Exception as e:
            print(e)
            url_data.append([None, 00.0, '', url[0], str(e)])
            q.task_done()


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
            sys.exit(1)
