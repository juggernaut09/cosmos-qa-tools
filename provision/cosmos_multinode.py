import sys
import os

# read no.of nodes and accounts to be setup
if len(sys.argv):
    NODES = 2
    ACCOUNTS = 100
else:
    NODES = int(sys.argv[1])
    ACCOUNTS = int(sys.argv[2])

print(" ** Number of nodes : {0} and accounts : {1} to be setup **".format(NODES, ACCOUNTS))
print("**** Number of nodes to be setup: {} ****".format(NODES))
os.chdir(os.path.expanduser('~'))
print("--------- Install cosmovisor-------")


