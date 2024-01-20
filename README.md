# otx_to_rapid7

## Requirements

You need a OTX account with a api key and at least on subscribed stream, use Alienvault (tends to be fairly good and uncluttered)
You need a Rapid7 API key with access to the community threat feed

Python3 Installed
Modules required: json, requests

## Aims of this script

to continously monitor all subscribed pulses and create the threat feed automagically
it will have basic tracking so it would constanting try to spam rapid7