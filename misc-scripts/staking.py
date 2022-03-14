import os
import argparse
import requests as req
import json
import subprocess
import time

from dotenv import load_dotenv

load_dotenv()

parser = argparse.ArgumentParser()

def node_type(x):
    x = int(x)
    if x < 2:
        raise argparse.ArgumentTypeError(f"The number of nodes should be Min. 2, you have entered {x}")
    return x

parser.add_argument('nodes', type= node_type, help= 'Number of nodes should be Min. 2 should be given')

args = parser.parse_args()
print(f"**** Number of nodes mentioned: {args.nodes} *****")

resp = req.get('https://ipinfo.io/ip')
IP = resp.text

if not IP:
     IP='127.0.0.1'

print("------------Delegation tx----------------\n")
DAEMON = os.getenv('DAEMON')
DAEMON_HOME= os.getenv('DAEMON_HOME')
CHAINID = os.getenv('CHAINID')
DENOM = os.getenv('DENOM')
for a in range(1,args.nodes):
    DIFF = a-1
    INC = DIFF*2
    PORT = 16657 + INC
    RPC = f"http://{IP}:{PORT}"
    TONODE = 1 + a
    validator = f"{DAEMON} keys show validator{TONODE} --bech val --keyring-backend test --home {DAEMON_HOME}-{TONODE} --output json"
    process = subprocess.Popen(validator.split(), stdout=subprocess.PIPE, text=True)
    output, error = process.communicate()
    res = (json.loads(output))
    VALADDRESS = res["address"]
    FROMKEY = "validator{a}"
    TO, TOKEY = VALADDRESS,f"validator{TONODE}"
    print(f"** to validator address :: {TO} and from key :: {FROMKEY} **")
    print (f"Iteration no {a} and values of from : {FROMKEY} to : {TO}")
    print(f"--------- Delegation from {FROMKEY} to {TO}-----------")
    dTx = f"{DAEMON} tx staking delegate {TO} 10000{DENOM} --from {FROMKEY} --fees 1000{DENOM} --chain-id {CHAINID} --keyring-backend test --home {DAEMON_HOME}-{a} --node {RPC} --output json -y"
    process = subprocess.Popen(dTx.split(), stdout=subprocess.PIPE, text=True)
    output, error = process.communicate()
    time.sleep(6)
    res = (json.loads(output))
    dtxHash = res["txhash"]
    print(f"** TX HASH :: {dtxHash} **")
    txResult=f"{DAEMON} q tx {dtxHash} --node {RPC} --output json"
    process = subprocess.Popen(txResult.split(), stdout=subprocess.PIPE, text=True)
    output, error = process.communicate()
    res = (json.loads(output))
    dTxCode = res["code"]
    reason = res["raw_log"]
    if dTxCode == 0:
        print(f"**** Delegation from {FROMKEY} to {TOKEY} is SUCCESSFULL!!  txHash is : {dtxHash} ****\n")
    else:
        print(f"**** Delegation from {FROMKEY} to {TOKEY} has FAILED!!!!   txHash is : {dtxHash} and REASON : {reason}\n")
    
print(f"-----------Redelegation txs-------------\n")
for a in range(args.nodes,0,-1):
    if a == 1:
        N = args.nodes
        P = N - 1
        fromValidator = f"{DAEMON} keys show validator{N} --bech val --keyring-backend test --home {DAEMON_HOME}-{N} --output json"
        process = subprocess.Popen(fromValidator.split(), stdout=subprocess.PIPE, text=True)
        output, error = process.communicate()
        res = json.loads(output)
        FROMADDRESS = res["address"]
        toValidator = f"{DAEMON} keys show validator{P} --bech val --keyring-backend test --home {DAEMON_HOME}-{P} --output json"
        process = subprocess.Popen(toValidator.split(), stdout=subprocess.PIPE, text=True)
        output, error = process.communicate()
        res = json.loads(output)
        TOADDRESS = res["address"]
        FROM = FROMADDRESS
        TO = TOADDRESS
        FROMKEY = f"validator{N}"
        TOKEY = f"validator{P}"
    else:
        DIFF = a-1
        INC = DIFF*2
        PORT = 16657 + INC
        RPC = f"http://{IP}:{PORT}"
        TONODE = a - 1
        fromValidator = f"{DAEMON} keys show validator{a} --bech val --keyring-backend test --home {DAEMON_HOME}-{a} --output json"
        process = subprocess.Popen(fromValidator.split(), stdout=subprocess.PIPE, text=True)
        output, error = process.communicate()
        res = json.loads(output)
        FROMADDRESS = res["address"]
        toValidator = f"{DAEMON} keys show validator{TONODE} --bech val --keyring-backend test --home {DAEMON_HOME}-{TONODE} --output json"
        process = subprocess.Popen(toValidator.split(), stdout=subprocess.PIPE, text=True)
        output, error = process.communicate()
        res = json.loads(output)
        TOADDRESS = res["address"]
        FROM = FROMADDRESS
        TO = TOADDRESS
        FROMKEY = f"validator{a}"
        TOKEY = f"validator{TONODE}"
        print(f"** validator address :: {VALADDRESS} and from key :: {FROMKEY} **")

    print(f"Iteration no {a} and values of from : {FROMKEY} to : {TOKEY}\n")
    print(f"--------- Redelegation from {FROM} to {TO}-----------\n")
    rdTx = f"{DAEMON} tx staking redelegate {FROM} {TO} 10000{DENOM} --from {FROMKEY} --fees 1000{DENOM} --gas 400000 --chain-id {CHAINID} --keyring-backend test --home {DAEMON_HOME}-{a} --node {RPC} --output json -y"
    process = subprocess.Popen(rdTx.split(), stdout=subprocess.PIPE, text=True)
    output, error = process.communicate()
    returncode = process.wait()
    if returncode != 0:
        print(f"**** Redelegation from {FROMKEY} to {TOKEY} has FAILED!!!!")
    else:
        time.sleep(6)
        res = json.loads(output)
        rdtxHash = res["txhash"]
        print(f"** TX HASH :: {rdtxHash} **")
        txResult=f"{DAEMON} q tx {rdtxHash} --node {RPC} --output json"
        process = subprocess.Popen(txResult.split(), stdout=subprocess.PIPE, text=True)
        output, error = process.communicate()
        res = json.loads(output)
        rdTxCode = res["code"]
        reason = res["raw_log"]
        if rdTxCode == 0:
            print(f"**** Redelegation from {FROMKEY} to {TOKEY} is SUCCESSFULL!!  txHash is : {rdtxHash} ****\n")
        else:
            print(f"**** Redelegation from {FROMKEY} to {TOKEY} has FAILED!!!!  txHash is : {rdtxHash} and REASON : {reason}\n")

print("--------- Unbond txs -----------\n")
for a in range(1,args.nodes):
    DIFF = a-1
    INC = DIFF*2
    PORT = 16657 + INC
    RPC = "http://"+str(IP)+":"+str(PORT)
    validator = f"{DAEMON} keys show validator{a} --bech val --keyring-backend test --home {DAEMON_HOME}-{a} --output json"
    process = subprocess.Popen(validator.split(), stdout=subprocess.PIPE, text=True)
    output, error = process.communicate()
    res = json.loads(output)
    VALADDRESS=res["address"]
    FROM=VALADDRESS
    FROMKEY=f"validator{a}"
    print(f"** validator address :: {FROM} and From key :: {FROMKEY} **")
    print(f"Iteration no {a} and values of from : {FROM} and fromKey : {FROMKEY}")
    print(f"--------- Running unbond tx command of {FROM} and key : {FROMKEY}------------")
    ubTx=f"{DAEMON} tx staking unbond {FROM} 10000{DENOM} --from {FROMKEY} --fees 1000{DENOM} --chain-id {CHAINID} --keyring-backend test --home {DAEMON_HOME}-{a} --node {RPC} --output json -y"
    process = subprocess.Popen(ubTx.split(), stdout=subprocess.PIPE, text=True)
    output, error = process.communicate()
    time.sleep(6)
    res = json.loads(output)
    ubtxHash = res["txhash"]
    print(f"** TX HASH :: {ubtxHash} **")
    txResult=f"{DAEMON} q tx {ubtxHash} --node {RPC} --output json"
    process = subprocess.Popen(txResult.split(), stdout=subprocess.PIPE, text=True)
    output, error = process.communicate()
    res = json.loads(output)
    ubTxCode = res["code"]
    reason = res["raw_log"]

    if ubTxCode == 0:
        print(f"**** Unbond tx ( of {FROM} and key {FROMKEY} ) is SUCCESSFULL!!  txHash is : {ubtxHash} ****\n")
    else:
        print(f"**** Unbond tx ( of {FROM} and key {FROMKEY} ) FAILED!!!!   txHash is : {ubtxHash}  and REASON : {reason} ***\n")
