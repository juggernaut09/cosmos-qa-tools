import os
import argparse
import requests as req
import subprocess

from dotenv import load_dotenv

load_dotenv()

parser = argparse.ArgumentParser()

def num_nodes(x):
    x = int(x)
    if x < 1:
        raise argparse.ArgumentTypeError(f"The number of nodes should be Min. 1, you have entered {x}")
    return x

parser.add_argument('nodes', type= num_nodes, help= 'Number of nodes to be shutdown. Min. 1 should be given')

args = parser.parse_args()
print("**** Number of nodes to be shutdown and disabled: %d *****",args.nodes)

print("---------- Stopping systemd service files ------------")
d = os.getenv('DAEMON')
for a in range(args.nodes):
    id = d + "-" + str(a)+".service"
    cmd = "sudo -S systemctl stop " + id
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    print("--- Stopped " + id +" ----")

print("-------- Running unsafe reset all -----------")
for a in range(args.nodes):
    id = d + "-" + str(a)
    rescmd = d + " unsafe-reset-all" + " --home " + id
    process = subprocess.Popen(rescmd.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    cmd = "rm -rf " + id 
    proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    out, error = proc.communicate()

    print("--- Execute " + d + "unsafe-reset-all "+ "--home " + id + " ---")

print("------- Disabling systemd process files -------")
for a in range(args.nodes):
    id = d + "-" + str(a)+".service"
    cmd = "sudo -S systemctl disable " + id
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    print("-- Execute sudo -S systemctl disable " + id + " --") 
