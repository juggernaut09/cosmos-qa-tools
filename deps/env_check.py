import os
import sys

def display_usage():
    s = ""
    s += "DAEMON \n" if 'DAEMON' not in os.environ.keys() else ""
    s += "DENOM \n" if 'DENOM' not in os.environ.keys() else ""
    s += "CHAINID \n" if 'CHAINID' not in os.environ.keys() else ""
    s += "DAEMON_HOME \n" if 'DAEMON_HOME' not in os.environ.keys() else ""
    s += "GH_URL \n" if 'GH_URL' not in os.environ.keys() else ""
    s += "CHAIN_VERSION \n" if 'CHAIN_VERSION' not in os.environ.keys() else ""
    
    if not len(s):
        print("** These are the environment variables exported : \n")
        print("1. DAEMON = {}\n2. DENOM = {}\n3. CHAINID = {}\n4. DAEMON_HOME = {}\n5. GH_URL = {}\n6. CHAIN_VERSION = {}\n".format(os.environ['DAEMON'], os.environ['DENOM'], os.environ['CHAINID'], os.environ['DAEMON_HOME'], os.environ['GH_URL'], os.environ['CHAIN_VERSION']))
    else:
        print("** Please export all the necessary env variables  :: \n")
        print(s)
    sys.exit()

display_usage()



