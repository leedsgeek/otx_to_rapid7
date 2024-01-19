import requests

def get_pulse():
  url = "https://otx.alienvault.com/api/v1/pulses/subscribed"
  payload = {}
  headers = {
    'X-OTX-API-KEY': ''
  }

  response = requests.request("GET", url, headers=headers, data=payload)
  return response.json()

def log_ids(pulsedata):
  id_list = []
  for key,value in pulsedata.items():
    if key == 'results':
      collection=value
      for x in collection:
        id_list.append(x['id'])
  return id_list

def get_indicators(pulsedata):
  for key,value in pulsedata.items():
    if key == 'results':
      collection=value
      print(collection)
      for x in collection:
        print(x['id'])
        print(x['name'])
        ind = x['indicators']
        for indv in ind:
          print(indv['indicator'])



pulsedata = get_pulse()
pulse_id = log_ids(pulsedata)
if not pulse_id:
  print("Not IDs Found")
else:
  print("List Not Empty")
