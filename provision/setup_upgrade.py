import argparse
import os
import subprocess
import sys
import shutil

from dotenv import dotenv_values

### Fetch env values
config = dotenv_values(".env")
DAEMON = config['DAEMON']
DENOM = config['DENOM']
CHAINID = config['CHAINID']
DAEMON_HOME = config['DAEMON_HOME']
GH_URL = config['GH_URL']
CHAIN_VERSION = config['CHAIN_VERSION']
UPGRADE_NAME = config['UPGRADE_NAME']
UPGRADE_VERSION = config['UPGRADE_VERSION']
HOME = config['HOME']

def node_type(x):
    x = int(x)
    if x < 2:
        raise argparse.ArgumentTypeError(f"The number of nodes should be Min. 2, you have entered {x}")
    return x

parser = argparse.ArgumentParser(description='This program takes inputs for intializing nodes configuration.')
parser.add_argument('nodes', type= node_type, help= 'Number of nodes to be upgraded. Min. 2 should be given')
args = parser.parse_args()
print(f" ** Number of nodes : {args.nodes} to be upgraded **")
os.environ['NODES'] = str(args.nodes)
os.chdir(os.path.expanduser('~'))

### Build the upgrade version
if not GH_URL:
    sys.exit('The environment varible \'GH_URL\' is None make sure to update the env values in .env file')

os.environ['REPO'] = GH_URL.split('/')[-1]
shutil.rmtree(f"{os.getenv('REPO')}")
subprocess.run(['git', 'clone', f"{GH_URL}"])
os.chdir(f"{os.getenv('REPO')}")
subprocess.run(['git', 'fetch'])
subprocess.run(['git', 'checkout', f"{UPGRADE_VERSION}"])
subprocess.run(['make', 'build'])

for i in range(1, int(os.getenv('NODES')) + 1):
    os.environ[f"DAEMON_HOME_{i}"] = f"{DAEMON_HOME}-{i}"
    os.makedirs(f"{DAEMON_HOME}-{i}/cosmovisor/upgrades/{UPGRADE_NAME}/bin")
    shutil.copy(f"{HOME}/{os.getenv('REPO')}/build/{UPGRADE_NAME}", f"{DAEMON_HOME}-{i}/cosmovisor/upgrades/{UPGRADE_NAME}/bin/")

print("-------- New upgraded binary is moved to cosmovisor ---------")