import argparse
import subprocess
import os
import sys
from dotenv import load_dotenv
load_dotenv()

def account_type(x):
    acc = f"{os.getenv('DAEMON')} keys show account{x} -a --home {os.getenv('DAEMON_HOME')}-1 --keyring-backend test"
    stdout, stderr = subprocess.Popen(acc.split(),
                                    stdout = subprocess.PIPE,
                                    stderr = subprocess.PIPE).communicate()
    if len(stderr):
        raise argparse.ArgumentTypeError(stderr.strip().decode())
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

print(f"FROM: {FROM}")
print(f"TO: {TO}")
print(f"NUM_TXS: {NUM_TXS}")

def balance_query(bech_address, RPC):
    command = f"{os.getenviron('DAEMON')} q bank balances {} --node {} --output json"
    balance = subprocess.Popen()






