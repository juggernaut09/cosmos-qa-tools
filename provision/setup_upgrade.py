import argparse
import os
import subprocess
import sys
import shutil


from dotenv import load_dotenv

load_dotenv()

def node_type(x):
    x = int(x)
    if x < 2:
        raise argparse.ArgumentTypeError(f"The number of nodes should be Min. 2, you have entered {x}")
    return x

parser = argparse.ArgumentParser(description='This program takes inputs for intializing nodes configuration.')
parser.add_argument('nodes', type= node_type, help= 'Number of nodes to be created. Min. 2 should be given')
args = parser.parse_args()
print(f" ** Number of nodes : {args.nodes} to be upgraded **")
os.environ['NODES'] = str(args.nodes)
os.chdir(os.path.expanduser('~'))

### Build the upgrade version
if not os.getenv('GH_URL'):
    sys.exit('The environment varible \'GH_URL\' is None make sure to update the env values in .env file')

os.environ['REPO'] = os.getenv('GH_URL').split('/')[-1]
os.rmdir(f"{os.getenv('REPO')}")
subprocess.run(['git', 'clone', f"{os.getenv('GH_URL')}"])
os.chdir(f"{os.getenv('REPO')}")
subprocess.run(['git', 'fetch'])
subprocess.run(['git', 'checkout', f"{os.getenv('UPGRADE_VERSION')}"])
subprocess.run(['make', 'build'])

for i in range(1, int(os.getenv('NODES')) + 1):
    os.environ[f"DAEMON_HOME_{i}"] = f"{os.getenv('DAEMON_HOME')}-{i}"
    os.makedirs(f"{os.getenv('DAEMON_HOME')}-{i}/cosmovisor/upgrades/{os.getenv('UPGRADE_NAME')}/bin")
    shutil.copy(f"{os.getenv('HOME')}/{os.getenv('REPO')}/build/{os.getenv('DAEMON')}", f"{os.getenv('DAEMON_HOME')}-{i}/cosmovisor/upgrades/{os.getenv('UPGRADE_NAME')}/bin/")

print("-------- New upgraded binary is moved to cosmovisor ---------")