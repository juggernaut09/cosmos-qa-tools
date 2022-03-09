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

parser.add_argument('nodes', type= num_nodes, help= 'Number of nodes to be resumed. Min. 1 should be given')

args = parser.parse_args()
print("**** Number of nodes to be resumed: %d *****",args.nodes)

print("---------- Restarting systemd service files ---------")
d = os.getenv('DAEMON')
for a in range(args.nodes):
      id = d + "-" + str(a)+".service"
      cmd = "sudo -S systemctl restart " + id
      print(cmd)
      process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
      output, error = process.communicate()
      print("--- Resumed " + id +" ----")

