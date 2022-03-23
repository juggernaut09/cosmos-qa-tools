This repo contains all python scripts which can be used for quickly setting up a local test environment for any Cosmos based network with n number of nodes and m number of accounts. It installs go if it's not already installed on the system and also installs all the dependencies along with it.

## Install the Python development environment on your system

```bash
python3 --version
pip3 --version
```

```bash
sudo apt update
sudo apt install python3-dev python3-pip python3-venv
```

## Create a virtual environment (recommended)

```bash
### Create a new virtual environment by choosing a Python interpreter and making a ./venv directory to hold it:
python3 -m venv --system-site-packages ./venv

### Activate the virtual environment using a shell-specific command:
source ./venv/bin/activate # When the virtual environment is active, your shell prompt is prefixed with (venv)
```

## Install packages within a virtual environment without affecting the host system setup. Start by upgrading pip:

```bash
pip install --upgrade pip

pip list  # show packages installed within the virtual environment
```

## Install the dependencies from requirements.txt

```bash
pip install -r requirements.txt
```

## And to exit the virtual environment later:

```bash
deactivate  # don't exit until you're done using dependencies.
```

## Make sure to import env values in .env file

> Note: .env file is not included. The file should be created. (Take below format as reference.)

```bash
DAEMON=gaiad
DENOM=uatom
CHAINID=test
DAEMON_HOME=${HOME}/.gaiad
GH_URL=https://github.com/cosmos/gaia
CHAIN_VERSION=v6.0.3
```

## Scripts:-

1. `cosmos_multinode.py` :- This script sets up the environment. It takes two arguments from the user. First argument is the number of nodes that need to be setup and the second argument is the number of additional accounts that need to be created.

2. Usage:-

```bash
python3 provision/cosmos_multinode.py --help
```
