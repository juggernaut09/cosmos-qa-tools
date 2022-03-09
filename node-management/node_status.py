import os
import argparse
import sys
import requests as req
import json

from dotenv import load_dotenv

load_dotenv()

parser = argparse.ArgumentParser()

def num_nodes(x):
    x = int(x)
    if x < 1:
        raise argparse.ArgumentTypeError(f"The number of nodes should be Min. 1, you have entered {x}")
    return x

parser.add_argument('nodes', type= num_nodes, help= 'Number of nodes for status check. Min. 1 should be given')

args = parser.parse_args()
print("**** Number of nodes for status checks:", args.nodes)

#os.environ['NODES'] = args.nodes

url = 'https://ipinfo.io/json'
resp = req.get(url)
l = json.loads(resp.text)
IP = l["ip"]

if not len(IP):
     IP='127.0.0.1'

print("------- Query node status -------")
for a in range(args.nodes):
    DIFF = a-1
    INC = DIFF*2
    PORT = 16657 + INC
    RPC = "http://"+str(IP)+":"+str(PORT)+"/status?"
    res = req.get(RPC)
    result = json.loads(res.text)
    height = result["result"]["sync_info"]["latest_block_height"]
    syncStatus = result["result"]["sync_info"]["catching_up"]
    print("** rpc: latest_block_height: catching_up **",RPC,height,syncStatus)
    