import os
import sys
from dotenv import load_dotenv

load_dotenv()
def display_usage():
    s = ""
    s += "DAEMON \n" if not os.getenv('DAEMON') else ""
    s += "DENOM \n" if not os.getenv('DENOM') else ""
    s += "CHAINID \n" if not os.getenv('CHAINID') else ""
    s += "DAEMON_HOME \n" if not os.getenv('DAEMON_HOME') else ""
    s += "GH_URL \n" if not os.getenv('GH_URL') else ""
    s += "CHAIN_VERSION \n" if not os.getenv('CHAIN_VERSION') else ""
    
    if not len(s):
        print("** These are the environment variables exported : \n")
        print("1. DAEMON = {}\n2. DENOM = {}\n3. CHAINID = {}\n4. DAEMON_HOME = {}\n5. GH_URL = {}\n6. CHAIN_VERSION = {}\n".format(os.environ['DAEMON'], os.environ['DENOM'], os.environ['CHAINID'], os.environ['DAEMON_HOME'], os.environ['GH_URL'], os.environ['CHAIN_VERSION']))
    else:
        print("** Please export all the necessary env variables in .env file :: \n")
        print(s)
    sys.exit()
display_usage()