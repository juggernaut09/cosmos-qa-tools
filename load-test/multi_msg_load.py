import argparse
import subprocess
import os
import sys
import json
import time
from dotenv import load_dotenv

load_dotenv()

def command_processor(command):
    stdout, stderr = subprocess.Popen(command.split(),
                                    stdout = subprocess.PIPE,
                                    stderr = subprocess.PIPE).communicate()
    return stdout.strip().decode(), stderr.strip().decode()

def fetch_bech_address(account_name):
    command = f"{os.getenv('DAEMON')} keys show {account_name} -a --home {os.getenv('DAEMON_HOME')}-1 --keyring-backend test" 
    return command_processor(command)

def account_type(x):
    stdout, stderr = fetch_bech_address(f"account{x}")
    if len(stderr):
        raise argparse.ArgumentTypeError(stderr)
    return int(x)

def num_txs_type(x):
    if int(x) < 1000:
        raise argparse.ArgumentTypeError('The argument NUM_TXS should be 1000 or more')
    return int(x)

parser = argparse.ArgumentParser(description='This program takes inputs for intializing multi message load test.')
parser.add_argument('FROM', type= account_type, help= 'From which account the transaction should be intialized')
parser.add_argument('TO', type= account_type, help= 'Reciever account number.')
parser.add_argument('NUM_TXS', type = num_txs_type, help= 'Number of transactions to be made, Min. should be 1000')

args = parser.parse_args()
FROM = int(args.FROM)
TO = int(args.TO)
NUM_TXS = int(args.NUM_TXS)

if FROM == TO:
    sys.exit('Error: The values of arguments "TO" and "FROM" are equal make sure to set different values')

# print(f"FROM: {FROM}")
# print(f"TO: {TO}")
# print(f"NUM_TXS: {NUM_TXS}")

def balance_query(bech_address, RPC):
    command = f"{os.getenv('DAEMON')} q bank balances {bech_address} --node {RPC} --output json" 
    return command_processor(command)

#### Fetching Bech addresses ######
RPC = "http://127.0.0.1:16657"
num_msgs = 30

acc1, acc1err = fetch_bech_address(f"account{FROM}")
if len(acc1err):
    sys.exit(acc1err)

acc2, acc2err = fetch_bech_address(f"account{TO}")
if len(acc2err):
    sys.exit(acc2err)

#### Print Balances ####
print("** Balance of Account 1 before send_load :: **")
balance, balanceerr = balance_query(acc1, RPC)
if len(balanceerr):
    sys.exit(balanceerr)
print(balance)

print("** Balance of Account 2 before send_load :: **")
balance, balanceerr = balance_query(acc2, RPC)
if len(balanceerr):
    sys.exit(balanceerr)
print(balance)

#### Sequences ####
os.chdir(os.path.expanduser('~'))
command = f"{os.getenv('DAEMON')} q account {acc1} --node {RPC} --output json"
seq1, seq1err = command_processor(command)
seq1 = json.loads(seq1)
if len(seq1err):
    sys.exit(seq1err)
seq1no = int(seq1['sequence'])

command = f"{os.getenv('DAEMON')} q account {acc2} --node {RPC} --output json"
seq2, seq2err = command_processor(command)
if len(seq2err):
    sys.exit(seq2err)
seq2 = json.loads(seq2)
seq2no = int(seq2['sequence'])

def write_json(file_name):
    with open(file_name, 'r+') as file:
            file_data = json.load(file)
            new_data = file_data["body"]["messages"][-1]
            file_data["body"]["messages"].append(new_data)
            file.seek(0)
            json.dump(file_data, file, indent = 4)

for i in range(0, int(NUM_TXS) + 1):
    unsignedTxto_command = f"{os.getenv('DAEMON')} tx bank send {acc1} {acc2} 1000000{os.getenv('DENOM')} --chain-id {os.getenv('CHAINID')} --output json --generate-only --gas 500000"
    unsignedTxto, unsignedTxtoerr = command_processor(unsignedTxto_command)
    if len(unsignedTxtoerr):
        sys.exit(unsignedTxtoerr) 

    with open('unsignedto.json', 'w') as outfile:
        json.dump(json.loads(unsignedTxto), outfile)
    
    unsignedTxfrom_command = f"{os.getenv('DAEMON')} tx bank send {acc2} {acc1} 1000000{os.getenv('DENOM')} --chain-id {os.getenv('CHAINID')} --output json --generate-only --gas 500000"
    unsignedTxfrom, unsignedTxfromerr = command_processor(unsignedTxfrom_command)
    if len(unsignedTxfromerr):
        sys.exit(unsignedTxfromerr)
    with open('unsignedfrom.json', 'w') as outfile:
        json.dump(json.loads(unsignedTxfrom), outfile)
    
    for j in range(0, int(num_msgs) + 1):
        write_json('unsignedto.json')
        write_json('unsignedfrom.json')

    ### seqto ###
    seqto = seq1no + i
    signTxto_command = f"{os.getenv('DAEMON')} tx sign unsignedto.json --from {acc1} --chain-id {os.getenv('CHAINID')} --keyring-backend test --home {os.getenv('DAEMON_HOME')}-1 --node {RPC} --signature-only=false --sequence {seqto} --gas 500000"
    signTxto, signTxtoerr = command_processor(signTxto_command)
    """
    Note: A Bug from cosmos-sdk 0.44.3 is redirecting the output to stderr instead of stdout for sign command. Please note that we are going further with signTxtoerr instead of signTxto.
    """
    # if len(signTxtoerr):
    #     sys.exit(signTxtoerr)
    with open('signedto.json', 'w') as outfile:
        json.dump(json.loads(signTxtoerr), outfile)
    print(f"signTxtoRES : {json.loads(signTxtoerr)}")

    broadcastto_command = f"{os.getenv('DAEMON')} tx broadcast signedto.json --output json --chain-id {os.getenv('CHAINID')} --gas 500000 --node {RPC} --broadcast-mode async"
    broadcastto, broadcasttoerr = command_processor(broadcastto_command)
    if len(broadcasttoerr):
        sys.exit(broadcasttoerr)
    broadcastto = json.loads(broadcastto)
    print(f"broadcasttoTxhash: {broadcastto['txhash']}")

    ### seqfrom ###
    seqfrom = seq2no + i
    signTxfrom_command = f"{os.getenv('DAEMON')} tx sign unsignedfrom.json --from {acc2} --chain-id {os.getenv('CHAINID')} --keyring-backend test --home {os.getenv('DAEMON_HOME')}-1 --node {RPC} --signature-only=false --sequence {seqfrom} --gas 500000"
    signTxfrom, signTxfromerr = command_processor(signTxfrom_command)
    """
    Note: A Bug from cosmos-sdk 0.44.3 is redirecting the output to stderr instead of stdout for sign command. Please note that we are going further with signTxfromerr instead of signTxfrom.
    """
    # if len(signTxfromerr):
    #     sys.exit(signTxfromerr)
    with open('signedfrom.json', 'w') as outfile:
        json.dump(json.loads(signTxfromerr), outfile)
    print(f"signTxfromRes : {json.loads(signTxfromerr)}")
    broadcastfrom_command = f"{os.getenv('DAEMON')} tx broadcast signedfrom.json --output json --chain-id {os.getenv('CHAINID')} --gas 500000 --node {RPC} --broadcast-mode async"
    broadcastfrom, broadcastfromerr = command_processor(broadcastfrom_command)
    if len(broadcastfromerr):
        sys.exit(broadcastfromerr)
    broadcastfrom = json.loads(broadcastfrom)
    print(f"broadcastfromTxhash: {broadcastfrom['txhash']}")

print('##### Sleeping for 7s #####')
time.sleep(7)
#### Print Balances ####
print("** Balance of Account 1 after send_load :: **")
balance, balanceerr = balance_query(acc1, RPC)
if len(balanceerr):
    sys.exit(balanceerr)
print(balance)

print("** Balance of Account 2 after send_load :: **")
balance, balanceerr = balance_query(acc2, RPC)
if len(balanceerr):
    sys.exit(balanceerr)
print(balance)