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

parser.add_argument('nodes', type= node_type, help= 'Number of nodes to be shutdown. Min. 1 should be given')

args = parser.parse_args()
print("**** Number of nodes to be shutdown and disabled: %d *****" % args.nodes)

print("---------- Stopping systemd service files ------------")

daemon = os.getenv('DAEMON')

for a in range(1,args.nodes+1):
    id = f"{daemon}-{a}.service"
    cmd = f"sudo -S systemctl stop {id}"
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    print(f"---- Stopped  {id}--------")

print("-------- Running unsafe reset all -----------")
for a in range(1,args.nodes+1):
    id = f"{daemon}-{a}.service"
    rescmd = f"{daemon} unsafe-reset-all --home {id}"
    process = subprocess.Popen(rescmd.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    
    cmd = f"rm -rf {id}"
    proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    out, error = proc.communicate()
    
    print(f"--- Executed {daemon} unsafe-reset-all --home {id} ---")
print("------- Disabling systemd process files -------")
for a in range(1,args.nodes+1):
    id = f"{daemon}-{a}.service"
    cmd = f"sudo -S systemctl disable {id}"
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    print(f"-- Executed sudo -S systemctl disable {id} --")
