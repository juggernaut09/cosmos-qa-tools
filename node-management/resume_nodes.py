import os
import argparse
import requests as req
import subprocess

from dotenv import load_dotenv

load_dotenv()

parser = argparse.ArgumentParser()

def node_type(x):
    x = int(x)
    if x < 1:
        raise argparse.ArgumentTypeError(f"The number of nodes should be Min. 1, you have entered {x}")
    return x

parser.add_argument('nodes', type= node_type, help= 'Number of nodes to be resumed. Min. 1 should be given')
args = parser.parse_args()

os.environ['NODES'] = str(args.nodes)

print(f"**** Number of nodes to be resumed: {args.nodes} *****")

print("---------- Restarting systemd service files ---------")
DAEMON = os.getenv('DAEMON')
for a in range(1,args.nodes+1):
    cmd = f"sudo -S systemctl restart {DAEMON}-{a}.service"
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    process.communicate()
    print(f"---- Restarted {DAEMON}-{a}.service--------")

