#!/usr/bin/python

import os
import sys
import re
import fileinput
import urllib2
import time
import ssl
import json

#filesource = "sources/list.txt"

filesource = os.environ['LIST'] 


def main():
  file = open_file()  
  for line in file:
    url = line.split(" ")
    try:
      url[2]
    except:
      warning = 0.1
    else:
      warning = url[2]
    try:
      url[3]
    except:
      danger = 0.2
    else:
      danger = url[3]
    time.sleep(2)
    format_response(url, danger, warning)
  time.sleep(30)


def format_response(url, danger, warning):
    retry = 0
    req, timereq, end = checkurl(url[0])
    # retry
    if req != None:
      timenow = time.strftime("%d/%m/%Y %H:%M:%S") 
      retcode = req.getcode()
      html = req.read()
      result = html.count(url[1])
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
    data_json = format_to_json(status_code, etat, timereq, url, retcode, result, message)
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
    data['url'] = url[0] 
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
  return req, timereq, end

  

if __name__ == '__main__':
  while True:
    try:
      main()
    except KeyboardInterrupt:
      exit(1)
