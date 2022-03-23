import argparse
import subprocess
import os
import sys
import json
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
        raise argparse.ArgumentTypeError('The argument num_txs should be 1000 or more')
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

#### Fetching Balance from accounts ######
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
seq1no = seq1['sequence']

command = f"{os.getenv('DAEMON')} q account {acc2} --node {RPC} --output json"
seq2, seq2err = command_processor(command)
if len(seq2err):
    sys.exit(seq2err)
seq2 = json.loads(seq2)
seq2no = seq2['sequence']







    






