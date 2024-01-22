import requests
import json
from datetime import datetime
import time
import logging
import sys
# Logging Module
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)
file_handler = logging.FileHandler('./otx_rapid7.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stdout_handler)
# Global Variables
rapid7_api_key = '[enter rapid7 api key]'
otx_key = '[Enter otx api key]'
file_types = ['FileHash-MD5']
region = '[enter region]'
log_id_post = []
# Get Only Subscribed Pulses
def get_pulse():
  url = "https://otx.alienvault.com/api/v1/pulses/subscribed"
  payload = {}
  headers = {
    'X-OTX-API-KEY': otx_key
  }
  try: 
    response = requests.request("GET", url, headers=headers, data=payload, timeout = 10, verify = True) 
    logger.info("Successfully Connected", str(url))
  except requests.exceptions.HTTPError as errh: 
    logger.error(errh.args[0])
  except requests.exceptions.ReadTimeout as errrt: 
    logger.error("Request Timed Out")
  except requests.exceptions.ConnectionError as conerr: 
    logger.error("Failed to Connect to alienvault")
  # Gets the response and converts to json to parse the data
  return response.json()

# Creates a list of ID to track and get indicators
def log_ids(pulsedata):
  id_list = []
  for key,value in pulsedata.items():
    if key == 'results':
      collection=value
      for x in collection:
        id_list.append(x['id'])
  return id_list

# creates a dict with all the data for a rapid7 request and then executes one its turned it to json
def get_indicators(pulse_id):
  for x in pulse_id:
    # Lists of values to be populated
    filehash = []
    domain = []
    www = []
    url = "https://otx.alienvault.com/api/v1/pulses/"+x
    payload = {}
    headers = { 'X-OTX-API-KEY': otx_key }
    try: 
      response = requests.request("GET", url, headers=headers, data=payload, timeout = 10, verify = True)
      logger.info(str(url)) 
    except requests.exceptions.HTTPError as errh: 
      logger.error(errh.args[0])
    except requests.exceptions.ReadTimeout as errrt: 
      logger.error("Request Timed Out")
    except requests.exceptions.ConnectionError as conerr: 
      logger.error("Failed to Connect to alienvault")
    resp = response.json()
    threat = {"threat": resp['name'],"note": "Information Scrape from OTX add to R7 By Adaresec"}
    for x in resp["indicators"]:
      # This collects file hashes
      if x['type'] in file_types:
        filehash.append(x["indicator"])
      # collects the domain names
      if x['type'] == "hostname":
          domain.append(x["indicator"])
      # Collects URLs
      if x['type'] == "URL":
          www.append(x["indicator"])
    # Creates the payload to send to rapid7 os return this
    threat['indicators']= {"hashes": filehash, "domain_names":domain, "urls":www}
    post_threat(threat,x)
# Attempts to publish threat to Rapid7
def post_threat(threat,x):
  if x['id'] in log_id_post:
    logger.info(str(x['id']), "Processed Already")
  else:
    url = "https://"+region+".api.insight.rapid7.com/idr/v1/customthreats"
    payload = json.dumps(threat)
    headers = {
      'X-API-Key': rapid7_api_key,
      'Content-Type': 'application/json',
    }
    try: 
      response = requests.request("POST", url, headers=headers, data=payload, timeout = 10)
      logger.info(str(url))
    except requests.exceptions.HTTPError as errh: 
      logger.error(errh.args[0])
    except requests.exceptions.ReadTimeout as errrt: 
      logger.error("Request Timed Out")
    except requests.exceptions.ConnectionError as conerr: 
      logger.error("Failed to Connect to Rapid7")
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code in ['200','400']:
      log_id_post.append(x['id'])
      print(log_id_post)
    else:
      logger.error("Unknown Response Code")    

while True:
  pulsedata = get_pulse()
  # pulse_id =["658481716d9034bb0d52212d"] # test ID which contains all indicators
  pulse_id = log_ids(pulsedata)
  if not pulse_id:
    print("Not IDs Found")
  else:
    print("List Not Empty")
    get_indicators(pulse_id)
    print("sleeping")
    time.sleep(60)
