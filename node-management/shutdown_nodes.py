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
print(f"**** Number of nodes to be shutdown and disabled: {args.nodes} *****")

print("---------- Stopping systemd service files ------------")

daemon = os.getenv('DAEMON')

for a in range(1,args.nodes+1):
    cmd = f"sudo -S systemctl stop {daemon}-{a}.service"
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    process.communicate()
    print(f"---- Stopped {daemon}-{a}.service--------\n")

print("-------- Running unsafe reset all ----------\n")
for a in range(1,args.nodes+1):
    rescmd = f"{daemon} unsafe-reset-all --home {daemon}-{a}.service"
    process = subprocess.Popen(rescmd.split(), stdout=subprocess.PIPE)
    process.communicate()
    
    cmd = f"rm -rf {daemon}-{a}.service"
    proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    proc.communicate()
    print(f"--- Executed {daemon} unsafe-reset-all --home {daemon}-{a}.service ---\n")
    
print("------- Disabling systemd process files -------\n")
for a in range(1,args.nodes+1):
    cmd = f"sudo -S systemctl disable {daemon}-{a}.service"
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    process.communicate()
    print(f"-- Executed sudo -S systemctl disable {daemon}-{a}.service --\n")
