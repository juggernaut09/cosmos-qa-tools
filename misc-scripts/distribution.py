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
print(f"**** Number of nodes mentioned: {args.nodes} *****\n")

resp = req.get('https://ipinfo.io/ip')
IP = resp.text

if not IP:
     IP='127.0.0.1'

print("---------- Run withdraw rewards tx -------\n")

DAEMON = os.getenv('DAEMON')
DAEMON_HOME= os.getenv('DAEMON_HOME')
CHAINID = os.getenv('CHAINID')
DENOM = os.getenv('DENOM')
for a in range(1,args.nodes+1):
    DIFF = a-1
    INC = DIFF*2
    PORT = 16657 + INC
    RPC = f"http://{IP}:{PORT}"
    validator = f"{DAEMON} keys show validator{a} --bech val --keyring-backend test --home {DAEMON_HOME}-{a} --output json"
    process = subprocess.Popen(validator.split(), stdout=subprocess.PIPE, text=True)
    output, error = process.communicate()
    errcode = process.wait()
    if errcode != 0:
        print(f"Error while gettig validator{a} address")
    else:
        res = (json.loads(output))
        VALADDRESS = res["address"]
        FROMKEY = f"validator{a}"
        print(f"** validator address :: {VALADDRESS} and From key :: {FROMKEY} **")
        print(f"Iteration no {a} and values of address : {VALADDRESS} and key : {FROMKEY}")

        print(f"--------- withdraw-rewards of {FROMKEY} -----------")
        wrTx = f"{DAEMON} tx distribution withdraw-rewards {VALADDRESS} --from {FROMKEY} --fees 1000{DENOM} --chain-id {CHAINID} --keyring-backend test --home {DAEMON_HOME}-{a} --node {RPC} --output json -y"
        process = subprocess.Popen(wrTx.split(), stdout=subprocess.PIPE, text=True)
        output, error = process.communicate()
        errcode = process.wait()
        time.sleep(6)
        if errcode != 0 :
            print(f"withdraw-rewards of {VALADDRESS} and key {FROMKEY} is failed!!!")
        else:
            res = json.loads(output)
            wrtxHash = res["txhash"]
            print(f"** TX HASH :: {wrtxHash} **")
            txResult = f"{DAEMON} q tx {wrtxHash} --node {RPC} --output json"
            process = subprocess.Popen(txResult.split(), stdout=subprocess.PIPE, text=True)
            output, error = process.communicate()
            try:
                res = json.loads(output)
                wrCode = res["code"]
                reason = res["raw_log"]
                if wrCode == 0:
                    print(f"**** withdraw-rewards of {VALADDRESS} and key {FROMKEY} is successfull!! txHash is : {wrtxHash} *****\n")
                else:
                    print(f"**** withdraw-rewards of {VALADDRESS} and key {FROMKEY} is failed!!! txHash is : {wrtxHash} and REASON : {reason} ****\n")
            except ValueError as e:
                print(f"{e}")
print("-----------Run withdraw-rewards commission txs ----------\n")
for a in range(1,args.nodes+1):
    DIFF = a-1
    INC = DIFF*2
    PORT = 16657 + INC
    RPC = f"http://{IP}:{PORT}"
    print(f"**** NODE :: {RPC} ******")
    validator = f"{DAEMON} keys show validator{a} --bech val --keyring-backend test --home {DAEMON_HOME}-{a} --output json"
    process = subprocess.Popen(validator.split(), stdout=subprocess.PIPE, text=True)
    output, error = process.communicate()
    errcode = process.wait()
    if errcode != 0:
        print(f"Error while getting validator{a} address")
    else:
        res = (json.loads(output))
        VALADDRESS = res["address"]
        FROMKEY = f"validator{a}"
        print(f"validator address :: {VALADDRESS} and From key :: {FROMKEY} **\n")
        print(f"Iteration no {a} and values of address: {VALADDRESS} and key : {FROMKEY}\n")

        print(f"--------- withdraw-rewards of {FROMKEY} -----------\n")
        wrcTx = f"{DAEMON} tx distribution withdraw-rewards {VALADDRESS} --from {FROMKEY} --commission --fees 1000{DENOM} --chain-id {CHAINID} --keyring-backend test --home {DAEMON_HOME}-{a} --node {RPC} --output json -y"
        process = subprocess.Popen(wrcTx.split(), stdout=subprocess.PIPE, text=True)
        output, error = process.communicate()
        ecode = process.wait()
        if ecode != 0:
            print(f"withdraw-rewards commission of {VALADDRESS} and key {FROMKEY} is failed!!!")
        else:
            time.sleep(6)
            res = json.loads(output)
            wrctxHash = res["txhash"]
            print(f"** TX HASH :: {wrctxHash} **")
            txResult = f"{DAEMON} q tx {wrctxHash} --node {RPC} --output json"
            process = subprocess.Popen(txResult.split(), stdout=subprocess.PIPE, text=True)
            output, error = process.communicate()
            try:
                res = json.loads(output)
                wrcCode = res["code"]
                reason = res["raw_log"]
                if wrcCode == 0:
                    print(f"**** withdraw-rewards commission of {VALADDRESS}and key {FROMKEY} is successfull!! txHash is : {wrctxHash} *****\n")
                else:
                    print(f"**** withdraw-rewards commission of {VALADDRESS} and key {FROMKEY} is failed!!! txHash is : {wrctxHash} and REASON: {reason} ****\n")
            except ValueError as e:
                print(f"withdraw-rewards commission of {VALADDRESS} and key {FROMKEY} is failed!!! Reason is : {e}")


print("--------- Run withdraw-all-rewards tx -----------\n")
for a in range(1,args.nodes+1):
    DIFF = a-1
    INC = DIFF*2
    PORT = 16657 + INC
    RPC = f"http://{IP}:{PORT}"
    print(f"**** NODE :: {RPC} ******")
    validator = f"{DAEMON} keys show validator{a} --bech val --keyring-backend test --home {DAEMON_HOME}-{a} --output json"
    process = subprocess.Popen(validator.split(), stdout=subprocess.PIPE, text=True)
    output, error = process.communicate()
    errcode = process.wait()
    if errcode != 0:
        print(f"Error while getting validator{a} address\n")
    else:
        res = (json.loads(output))
        VALADDRESS = res["address"]
        FROMKEY = f"validator{a}"
        print(f"** validator address :: {VALADDRESS} and From key :: {FROMKEY} **")
        print(f"Iteration no {a} and values of address : {VALADDRESS} and key : {FROMKEY}")
        print(f"--------- withdraw-all-rewards of {FROMKEY} -----------")
        warTx = f"{DAEMON} tx distribution withdraw-all-rewards --from {FROMKEY} --fees 1000{DENOM} --chain-id {CHAINID} --keyring-backend test --home {DAEMON_HOME}-{a} --node {RPC} --output json -y"
        process = subprocess.Popen(warTx.split(), stdout=subprocess.PIPE, text=True)
        output, error = process.communicate()
        ecode = process.wait()
        if ecode != 0:
            print(f"withdraw-all-rewards of {VALADDRESS} and key {FROMKEY} is failed!!!")
        else:
            time.sleep(6)
            res = json.loads(output)
            wartxHash = res["txhash"]
            print(f"** TX HASH :: {wartxHash}**")
            txResult = f"{DAEMON} q tx {wartxHash} --node {RPC} --output json"
            process = subprocess.Popen(txResult.split(), stdout=subprocess.PIPE, text=True)
            output, error = process.communicate()
            try:
                res = json.loads(output)
                warcode = res["code"]
                reason = res["raw_log"]
                if warcode == 0:
                    print(f"**** withdraw-all-rewards of {VALADDRESS} and key {FROMKEY} is successfull!! txHash is : {wartxHash} *****\n")
                else:
                    print(f"**** withdraw-all-rewards of {VALADDRESS} and key {FROMKEY} is failed!!! txHash is : {wartxHash} and REASON : {reason} ****\n")
            except ValueError as e:
                 print(f"**** withdraw-all-rewards of {VALADDRESS} and key {FROMKEY} is failed!!!  REASON : {e} ****")