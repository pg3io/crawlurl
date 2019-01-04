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

filesource = os.environ['LIST']
if environ.get('DELAY') is not None:
  delay = os.environ['DELAY']

url_data = []

def main():
  global url_data
  threads = []
  file = open_file()
  urls = get_url_array(file)

  while True:
    i = 0
    for url in urls:
      process = Thread(target=checkurl, args=[url])
      process.start()
      threads.append(process)
      for process in threads:
        process.join()

    for line in file:
      link = line.split(" ")
      try:
        link[2]
      except:
        warning = 0.1
      else:
        warning = link[2]
      try:
        link[3]
      except:
        danger = 0.2
      else:
        danger = link[3]
      format_response(urls[i], url_data[i][0], url_data[i][1], warning, danger, link[1])
      i += 1

    url_data = []
    if environ.get('DELAY') is not None:
      time.sleep(float(delay))
    else:
      time.sleep(30)


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
      status_code = 1
      message = "retry_or_%s_second_time_out" % danger
    elif result <= 0:
      etat = "danger"
      status_code = 1
      message = "no_word_in_page"
    elif timereq > warning:
      etat = "warning"
      status_code = 2
      message = "%s_second_time_out" % warning
    else:
      etat = "success"
      status_code = 0
      message = "ok"
  else:
    etat = "danger"
    status_code = 1
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
    data['result'] = result 
    data['message'] = message
    data_json = json.dumps(data)

    print(data_json)


def checkurl(url):
  try:
    start = time.time()
    req = urllib2.urlopen(url, timeout = 1)
    end = time.time()
    timereq = end - start
  except urllib2.HTTPError, e:
    #print("HTTPError ... url: %s code %s" % (url,e.code))
    end = time.time()
    return None, None, end 
  except urllib2.URLError, e:
    end = time.time()
    #print("URLError ... url: %s" % (url))
    return None, None, end
  except ssl.SSLError, e:
    #print("SSLError ... url: %s" % (url))
    end = time.time()
    return None, None, end

  url_data.append([req, timereq, end])

  return req, timereq, end



if __name__ == '__main__':
  while True:
    try:
      main()
    except KeyboardInterrupt:
      exit(1)
