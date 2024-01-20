import requests
import logging
import json

rapid7_api_key = '[Enter rapid7 api key]'
otx_key = '[Enter ATX API Key]'

file_types = ['FileHash-MD5']

# Get Only Subscribed Pulses
def get_pulse():
  url = "https://otx.alienvault.com/api/v1/pulses/subscribed"
  payload = {}
  headers = {
    'X-OTX-API-KEY': otx_key
  }
  try: 
    response = requests.request("GET", url, headers=headers, data=payload, timeout = 10, verify = True) 
    response.raise_for_status() 
  except requests.exceptions.HTTPError as errh: 
    print("HTTP Error") 
    print(errh.args[0]) 
  except requests.exceptions.ReadTimeout as errrt: 
    print("Time out") 
  except requests.exceptions.ConnectionError as conerr: 
    print("Connection error") 

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
  indicator_com = {}
  for x in pulse_id:
    filehash = []
    domain = []
    URL = []
    url = "https://otx.alienvault.com/api/v1/pulses/"+x
    payload = {}
    headers = { 'X-OTX-API-KEY': otx_key }
    response = requests.request("GET", url, headers=headers, data=payload)
    resp = response.json()
    threat = {"threat": resp['name'],"note": "Provided By OTX by AdareSEC"}
    for x in resp["indicators"]:
      # This collects file hashes
      if x['type'] in file_types:
        filehash.append(x["indicator"])
      # collects the domain names
      if x['type'] == "hostname":
          domain.append(x["indicator"])
      # Collects URLs
      if x['type'] == "URL":
          URL.append(x["indicator"])
      
    # Creates the payload to send to rapid7 os return this
    threat['indicators']= {"hashes": filehash, "domain_names":domain, "urls":URL}
    post_threat(threat,x)

def post_threat(threat,x):
  print(x["id"])
  url = "https://[Enter Region].api.insight.rapid7.com/idr/v1/customthreats"
  payload = json.dumps(threat)
  print(payload)
  headers = {
    'X-API-Key': rapid7_api_key,
    'Content-Type': 'application/json',
  }
  
  #response = requests.request("POST", url, headers=headers, data=payload)
  #print(response.text)
  #print(threat)

pulsedata = get_pulse()
# pulse_id =["658481716d9034bb0d52212d"] # test ID which contains all indicators
#pulse_id = log_ids(pulsedata)
#if not pulse_id:
#  print("Not IDs Found")
#else:
#  print("List Not Empty")
#  get_indicators(pulse_id)
