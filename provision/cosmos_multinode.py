import argparse
from cmath import e
import os
import subprocess
import sys
import shutil

from dotenv import load_dotenv
from subprocess import check_output

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
    try:
        shutil.rmtree(f"{os.getenv('DAEMON_HOME')}-{i}")
        print(f"Deleting existing daemon directory {os.getenv('DAEMON_HOME')}-{i}")
    except FileNotFoundError:
        print(f"The directory {os.getenv('DAEMON_HOME')}-{i} does not exists")


### Creating daemon home directories
print("-----Creating daemon home directories------")
for i in range(1, int(os.getenv('NODES'))+1):
    print(f"****** create dir :: {os.getenv('DAEMON_HOME')}-{i} ********\n")
    try:
        os.mkdir(f"{os.getenv('DAEMON_HOME')}-{i}")
        os.makedirs(f"{os.getenv('DAEMON_HOME')}-{i}/cosmovisor/genesis/bin")
    except FileExistsError as e:
        print(e)
    except FileNotFoundError as e:
        sys.exit(e) 
    shutil.copy(src=f"{shutil.which(os.getenv('DAEMON'))}", dst=f"{os.getenv('DAEMON_HOME')}-{i}/cosmovisor/genesis/bin/")

### --------Start initializing the chain CHAINID ---------
print(f"--------Start initializing the chain {os.getenv('CHAINID')}---------")
for i in range(1, int(os.getenv('NODES'))+1):
    print(f"-------Init chain {i}--------")
    print(f"Deamon home :: {os.getenv('DAEMON_HOME')}-{i}")
    subprocess.run([f"{os.getenv('DAEMON')}", 'init', '--chain-id', f"{os.getenv('CHAINID')}", f"{os.getenv('DAEMON_HOME')}-{i}", '--home', f"{os.getenv('DAEMON_HOME')}-{i}"])

### ------------Creating $NODES keys---------------
print(f"---------Creating {os.getenv('NODES')} keys-------------")
for i in range(1, int(os.getenv('NODES')) + 1):
    subprocess.run([f"{os.getenv('DAEMON')}", 'keys', 'add', f"validator{i}", '--keyring-backend', 'test', '--home', f"{os.getenv('DAEMON_HOME')}-{i}"])

### add accounts if second argument is passed
if not int(os.getenv('ACCOUNTS')):
    print("----- Argument for accounts is not present, not creating any additional accounts --------")
else:
    print(f"---------Creating {os.getenv('ACCOUNTS')} accounts-------------")
    for i in range(1, int(os.getenv('ACCOUNTS')) + 1):
        subprocess.run([f"{os.getenv('DAEMON')}", 'keys', 'add', f"account{i}", '--keyring-backend', 'test', '--home', f"{os.getenv('DAEMON_HOME')}-{i}"])

### ----------Genesis creation---------
print("----------Genesis creation---------")
for i in range(1, int(os.getenv('NODES')) + 1):
    if i == 1:
        subprocess.run([f"{os.getenv('DAEMON')}", '--home', f"{os.getenv('DAEMON_HOME')}-{i}", 'add-genesis-account', f"validator{i}", f"1000000000000{os.getenv('DENOM')}", '--keyring-backend', 'test'])
        print(f"done {os.getenv('DAEMON_HOME')}-{i} genesis creation")
        continue
    subprocess.run([f"{os.getenv('DAEMON')}", '--home', f"{os.getenv('DAEMON_HOME')}-{i}", 'add-genesis-account', f"validator{i}", f"1000000000000{os.getenv('DENOM')}", '--keyring-backend', 'test'])
    key_address = check_output([f"{os.getenv('DAEMON')}", 'keys', 'show', f"validator{i}", '-a', '--home', f"{os.getenv('DAEMON_HOME')}-{i}", '--keyring-backend', 'test'])
    address = key_address.strip().decode()
    subprocess.run([f"{os.getenv('DAEMON')}", '--home', f"{os.getenv('DAEMON_HOME')}-1", 'add-genesis-account', f"{address}", f"1000000000000{os.getenv('DENOM')}"])
print(f"--------Genesis created for {os.getenv('NODES')} nodes")