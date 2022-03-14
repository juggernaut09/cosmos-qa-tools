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

print(f"****** No.of validators who have to vote on the proposal : {args.nodes} ******")

resp = req.get('https://ipinfo.io/ip')
IP = resp.text

if not IP:
     IP='127.0.0.1'

print("--------Get voting period proposals--------------")
DAEMON = os.getenv('DAEMON')
DAEMON_HOME= os.getenv('DAEMON_HOME')
DENOM=os.getenv('DENOM')
CHAINID = os.getenv('CHAINID')
for port in range(1,args.nodes+1):
    DIFF = port-1
    INC = DIFF*2
    PORT = 16657 + INC
    NODE = f"http://{IP}:{PORT}"
vp = f"{DAEMON} q gov proposals --status voting_period --node {NODE} --output json"
process = subprocess.Popen(vp.split(), stdout=subprocess.PIPE, text=True)
output, error = process.communicate()
returncode = process.wait()   
if returncode != 0:
    print("No Proposals Found")
else: 
    res = json.loads(output)
    pres = res["proposals"]
    plen = len(pres)
    print("** Length of voting period proposals : %d" % plen)
    for row in pres:
        for i in row:
            PID = row["proposal_id"]
            print(f"** Checking votes for proposal id : {PID} **\n")
            for a in range(1,args.nodes+1):
                DIFF = a-1
                INC = DIFF*2
                PORT = 16657 + INC
                RPC = f"http://{IP}:{PORT}"
                validator = f"{DAEMON} keys show validator{a} --bech val --keyring-backend test --home {DAEMON_HOME}-{a} --output json"
                process = subprocess.Popen(validator.split(), stdout=subprocess.PIPE, text=True)
                output, error = process.communicate()
                res = (json.loads(output))
                VALADDRESS = res["address"]
                FROMKEY = "validator"+str(a)
                VOTER = VALADDRESS
                print(f"** validator address :: {VALADDRESS} and From key :: {FROMKEY} **")  
                getVote = f"{DAEMON} q gov vote {PID} {VOTER} --output json"
                process = subprocess.Popen(getVote.split(), stdout=subprocess.PIPE, text=True)
                output, error = process.communicate()
                res = (json.loads(output))
                returncode = process.wait()
                if returncode == 0:
                    voted = getVote["vote"]["option"]
                    castVote = f"{DAEMON} tx gov vote {PID} yes --from {FROMKEY} --fees 1000{DENOM} --chain-id {CHAINID} --node {RPC} --home {DAEMON_HOME}-{a} --keyring-backend test --output json -y"
                    process = subprocess.Popen(castVote.split(), stdout=subprocess.PIPE, text=True)
                    output, error = process.communicate()
                    res = json.loads(output)
                    time.sleep(6)
                    txHash = res["txhash"]
                    print(f"** TX HASH :: {txHash} **")
                    txResult = f"{DAEMON} q tx {txHash} --node {RPC} --output json"
                    process = subprocess.Popen(txResult.split(), stdout=subprocess.PIPE, text=True)
                    output, error = process.communicate()
                    res = json.loads(output)
                    checkVote = res["code"]
                    reason = res["raw_log"]
                    if checkVote != "":
                        if checkVote == 0:
                            print(f"**** {FROMKEY} successfully voted on the proposal :: (proposal ID : {PID} and address {VOTER})!! txHash is : {txHash}*****\n")
                        else:
                            print(f"**** {FROMKEY} getting error while casting vote for ( Proposl ID : {PID} and address {VOTER})!!! txHash is : {txHash} and REASON : {reason} ****\n")
                    else:
                        print(f"Error while getting votes of proposal ID : {PID} from {FROMKEY} address: {VOTER}\n")






                