import os
import argparse
import requests as req
import json

from dotenv import load_dotenv
load_dotenv()
parser = argparse.ArgumentParser()
def node_type(x):
    x = int(x)
    if x < 1:
        raise argparse.ArgumentTypeError(f"The number of nodes should be Min. 1, you have entered {x}")
    return x

parser.add_argument('nodes', type= node_type, help= 'Number of nodes for status check. Min. 1 should be given')
args = parser.parse_args()
print(f"**** Number of nodes for status checks: {args.nodes} ********")
os.environ['NODES'] = str(args.nodes)
resp = req.get('https://ipinfo.io/ip')
IP = resp.text
if not IP:
     IP='127.0.0.1'

print("------- Query node status -------")
for a in range(1,args.nodes+1):
    DIFF = a-1
    INC = DIFF*2
    PORT = 16657 + INC
    RPC = f"http://{IP}:{PORT}/status?"
    res = req.get(RPC)
    try:
       result = json.loads(res.text)
       height = result["result"]["sync_info"]["latest_block_height"]
       syncStatus = result["result"]["sync_info"]["catching_up"]
       print(f"** node: {a} rpc: {RPC} latest_block_height: {height} catching_up: {syncStatus}")
    except ValueError as e:
        print(e)