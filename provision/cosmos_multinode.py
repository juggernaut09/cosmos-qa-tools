import argparse
import os
import subprocess
import sys
import shutil
import requests
import time

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
        subprocess.run([f"{os.getenv('DAEMON')}", 'keys', 'add', f"account{i}", '--keyring-backend', 'test', '--home', f"{os.getenv('DAEMON_HOME')}-1"])

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
print(f"--------Genesis created for {os.getenv('NODES')} nodes-----------")

### "----------Genesis creation for accounts---------"

if not int(os.getenv('ACCOUNTS')):
    print("----- Argument for accounts is not present, not creating any additional accounts --------")
else:
    for i in range(1, int(os.getenv('ACCOUNTS')) + 1):
        key_address = check_output([f"{os.getenv('DAEMON')}", 'keys', 'show', f"account{i}", '-a', '--home', f"{os.getenv('DAEMON_HOME')}-1", '--keyring-backend', 'test'])
        address = key_address.strip().decode()
        print(f"cmd ::{os.getenv('DAEMON')} --home {os.getenv('DAEMON_HOME')}-1 add-genesis-account {address} 1000000000000{os.getenv('DENOM')}")
        subprocess.run([f"{os.getenv('DAEMON')}", '--home', f"{os.getenv('DAEMON_HOME')}-1", 'add-genesis-account', f"{address}", f"1000000000000{os.getenv('DENOM')}"])
    print("----------Genesis created for accounts---------")

### "--------Gentx--------"
print("--------Gentx--------")
for i in range(1, int(os.getenv('NODES')) + 1):
    subprocess.run([f"{os.getenv('DAEMON')}", 'gentx', f"validator{i}", f"90000000000{os.getenv('DENOM')}", '--chain-id', f"{os.getenv('CHAINID')}", '--keyring-backend', 'test', '--home', f"{os.getenv('DAEMON_HOME')}-{i}"])

### "---------Copy all gentxs to $DAEMON_HOME-1----------"
print(f"---------Copy all gentxs to {os.getenv('DAEMON_HOME')}-1----------")
for i in range(2, int(os.getenv('NODES')) + 1):
    source_directory_path = f"{os.getenv('DAEMON_HOME')}-{i}/config/gentx"
    destination_directory_path = f"{os.getenv('DAEMON_HOME')}-1/config/gentx"
    for source_filename in os.listdir(source_directory_path):
        if source_filename.endswith(".json"):
            source_file_path = os.path.join(source_directory_path, source_filename)
            shutil.copy(source_file_path, destination_directory_path)

### "----------collect-gentxs------------"
subprocess.run([f"{os.getenv('DAEMON')}", 'collect-gentxs', '--home', f"{os.getenv('DAEMON_HOME')}-1"])

print(f"---------Updating ${os.getenv('DAEMON_HOME')}-1 genesis.json ------------")
subprocess.run(['sed', '-i', 's/172800000000000/600000000000/g', f"{os.getenv('DAEMON_HOME')}-1/config/genesis.json"])
subprocess.run(['sed', '-i', 's/172800s/600s/g', f"{os.getenv('DAEMON_HOME')}-1/config/genesis.json"])
subprocess.run(['sed', '-i', f"s/stake/{os.getenv('DENOM')}/g", f"{os.getenv('DAEMON_HOME')}-1/config/genesis.json"])

print(f"---------Distribute genesis.json of {os.getenv('DAEMON_HOME')}-1 to remaining nodes-------")
for i in range(2, int(os.getenv('NODES')) + 1):
    shutil.copy(f"{os.getenv('DAEMON_HOME')}-1/config/genesis.json", f"{os.getenv('DAEMON_HOME')}-{i}/config/")

print(f"---------Getting public IP address-----------")
r = requests.get('https://ipinfo.io/ip')
IP = r.text

if not IP:
    IP = "127.0.0.1"

print(f"IP : {IP}")

### Arranging PERSISTENT_PEERS

print("-------Arranging PERSISTENT_PEERS---------")
for i in range(1, int(os.getenv('NODES')) + 1):
    DIFF = i - 1
    INC = DIFF * 2
    LADDR = 16656 + INC
    print(f"----------Get node-id of {os.getenv('DAEMON_HOME')}-$a ---------")
    encoded_nodeid = check_output([f"{os.getenv('DAEMON')}", 'tendermint', 'show-node-id', '--home', f"{os.getenv('DAEMON_HOME')}-{i}"])
    nodeID = encoded_nodeid.strip().decode()
    print(f"** Node ID :: {nodeID} **")
    PR=f"{nodeID}@{IP}:{LADDR}"
    if i == 1:
        PERSISTENT_PEERS=f"{PR}"
        continue
    PERSISTENT_PEERS=f"{PERSISTENT_PEERS},{PR}"

###updating config.toml
print("--------updating config.toml----------")
for i in range(1, int(os.getenv('NODES')) + 1):
    DIFF = i - 1
    INC = DIFF * 2
    RPC = 16657 + INC
    LADDR = 16656 + INC
    GRPC = 9090 + INC
    WGRPC = 9091 + INC
    print(f"----------Updating {os.getenv('DAEMON_HOME')}-{i} chain config-----------")
    subprocess.run(['sed', '-i', f"s#tcp://127.0.0.1:26657#tcp://0.0.0.0:{RPC}#g", f"{os.getenv('DAEMON_HOME')}-{i}/config/config.toml"])
    subprocess.run(['sed', '-i', f"s#tcp://0.0.0.0:26656#tcp://0.0.0.0:{LADDR}#g", f"{os.getenv('DAEMON_HOME')}-{i}/config/config.toml"])
    subprocess.run(['sed', '-i', f"/persistent_peers =/c\persistent_peers = \"{PERSISTENT_PEERS}\"", f"{os.getenv('DAEMON_HOME')}-{i}/config/config.toml"])
    subprocess.run(['sed', '-i', '/allow_duplicate_ip =/callow_duplicate_ip = true',  f"{os.getenv('DAEMON_HOME')}-{i}/config/config.toml"])
    subprocess.run(['sed', '-i', '/pprof_laddr =/c\# pprof_laddr = "localhost:6060"',  f"{os.getenv('DAEMON_HOME')}-{i}/config/config.toml"])
    subprocess.run(['sed', '-i', f"s#0.0.0.0:9090#0.0.0.0:{GRPC}#g",  f"{os.getenv('DAEMON_HOME')}-{i}/config/app.toml"])
    subprocess.run(['sed', '-i', f"s#0.0.0.0:9091#0.0.0.0:{WGRPC}#g",  f"{os.getenv('DAEMON_HOME')}-{i}/config/app.toml"])
    subprocess.run(['sed', '-i', '/max_num_inbound_peers =/c\max_num_inbound_peers = 140',  f"{os.getenv('DAEMON_HOME')}-{i}/config/config.toml"])
    subprocess.run(['sed', '-i', '/max_num_outbound_peers =/c\max_num_outbound_peers = 110',  f"{os.getenv('DAEMON_HOME')}-{i}/config/config.toml"])

print("Updated the configuration files")

### create system services

for i in range(1, int(os.getenv('NODES')) + 1):
    DIFF = i - 1
    INC = DIFF * 2
    RPC = 16657 + INC
    print(f"---------Creating {os.getenv('DAEMON_HOME')}-{i} system file---------")
    service_file = f"""
[Unit]
Description={os.getenv('DAEMON')} daemon
After=network.target

[Service]
Environment="DAEMON_HOME={os.getenv('DAEMON_HOME')}-{i}"
Environment="DAEMON_NAME={os.getenv('DAEMON')}"
Environment="DAEMON_ALLOW_DOWNLOAD_BINARIES=false"
Environment="DAEMON_RESTART_AFTER_UPGRADE=true"
Environment="UNSAFE_SKIP_BACKUP=false"
Type=simple
User={os.getenv('USER')}
ExecStart={shutil.which('cosmovisor')} start --home {os.getenv('DAEMON_HOME')}-{i}
Restart=on-failure
RestartSec=3
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target"""

    f = open(f"/lib/systemd/system/{os.getenv('DAEMON')}-{i}.service", "w+")
    f.write(service_file)
    f.close()
    print(f"-------Starting {os.getenv('DAEMON')}-{i} service-------")
    subprocess.run(['sudo', '-S', 'systemctl', 'daemon-reload'])
    subprocess.run(['sudo', '-S', 'systemctl', 'start', f"{os.getenv('DAEMON')}-{i}.service"])

print("-------------Taking time to initialize the chains-----------\n")
time.sleep(30)

for i in range(i, int(os.getenv('NODES')) + 1):
    DIFF = i - 1
    INC = DIFF * 2
    RPC = 16657 + INC
    print(f"Checking {os.getenv('DAEMON_HOME')}-{i} chain status")
    subprocess.run([f"{os.getenv('DAEMON')}", 'status', '--node', f"tcp://localhost:{RPC}"])

