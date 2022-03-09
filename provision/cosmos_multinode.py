import argparse
import os
import subprocess
import sys

from dotenv import load_dotenv
load_dotenv()

def node_type(x):
    x = int(x)
    if x < 2:
        raise argparse.ArgumentTypeError(f"The number of nodes should be Min. 2, you have entered {x}")
    return x

def is_tool(binary):
    """Check whether `name` is on PATH and marked as executable."""
    from shutil import which
    return which(binary) is not None

### Fetch NODES and ACCOUNTS values
parser = argparse.ArgumentParser(description='This program takes inputs for intializing nodes configuration.')
parser.add_argument('nodes', type= node_type, help= 'Number of nodes to be created. Min. 2 should be given')
parser.add_argument('accounts', type= int, help= 'Number of Accounts to be created. If not please enter 0')
args = parser.parse_args()
print(f" ** Number of nodes : {args.nodes} and accounts : {args.accounts} to be setup **")
os.environ['NODES'] = str(args.nodes)
os.environ['ACCOUNTS'] = str(args.accounts)
os.chdir(os.path.expanduser('~'))

### Cosmosvisor installation
print("--------- Install cosmovisor-------")
if is_tool('cosmovisor'):
    print("Found cosmovisor already installed.\n")
    print("Skipping the cosmosvisor installation.\n")
else:
    subprocess.run(['go', 'install', 'github.com/cosmos/cosmos-sdk/cosmovisor/cmd/cosmovisor@v1.0.0'])

subprocess.run(['which', 'cosmovisor']) # Print the cosmovisor location

if not os.getenv('GH_URL'):
    sys.exit('The environment varible \'GH_URL\' is None make sure to update the env values in .env file')

os.environ['REPO'] = os.getenv('GH_URL').split('/')[-1]


### DENOM Installation
print(f"--------- Install {os.getenv('DAEMON')} ---------")
if is_tool(os.getenv('DAEMON')):
    print(f"Found {os.getenv('DAEMON')} already installed.\n")
    print(f"Skipping the {os.getenv('DAEMON')} installation.\n")
else:
    subprocess.run(['git', 'clone', f"{os.getenv('GH_URL')}"])
    os.chdir(f"{os.getenv('REPO')}")
    subprocess.run(['git', 'fetch'])
    subprocess.run(['git', 'checkout', f"{os.getenv('CHAIN_VERSION')}"])
    subprocess.run(['make', 'install'])
    
os.chdir(os.path.expanduser('~'))
subprocess.run([f"{os.getenv('DAEMON')}", 'version', '--long']) # check DAEMON version

### export daemon home paths
for i in range(1, int(os.getenv('NODES')) + 1):
    os.environ[f'DAEMON_HOME_{i}'] = f"{os.getenv('DAEMON_HOME')}-{i}"
    print(f"Deamon path :: {os.getenv('DAEMON_HOME')}-{i}\n")
    print(f"****** here command {os.getenv('DAEMON')} unsafe-reset-all  --home {os.getenv('DAEMON_HOME')}-{i} ******")

### remove daemon home directories if it already exists
for i in range(1, int(os.getenv('NODES')) + 1):
    os.rmdir(f"{os.getenv('DAEMON_HOME')}-{i}")







