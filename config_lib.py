# helpers.py

from datetime import datetime
from config import *
import os
import yaml

# Config YAML file: (like in sample_config.yaml)
#
# To access diigo, we need an authenticated session as well as those parameters.
# The auth_timestamp records the last time the Diigo session was authenticated.

# Convert Unix time to datetime object
# unix_time = 1684915200  # Example Unix time
# datetime_obj = datetime.fromtimestamp(unix_time)

# print("Unix time:", unix_time)
# print("Datetime object:", datetime_obj)

def get_config(path):
    # Expand home directory
    path = os.path.expanduser(path)
    # Check whether there's a file with the passwords
    if os.path.exists(path):
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
        return(config)
    else: 
        return None

def write_config(path,config):
    path = os.path.expanduser(path)
    # Check whether directory exists and create if necessary
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.mkdir(directory)
    with open(path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False) 

def get_nc_key(path):
    path = os.path.expanduser(path)
    if os.path.exists(path):
        with open(path, "r") as file:
            nc_pass = file.read().strip()
            return nc_pass
    else:
        raise FileNotFoundError(f"Key file {path} not found")
    
def setup_config_dir():
    """
    If the key.YAML file in the .ncdbookmarks dir does not exist, 
    - create directory
    - copy sample YAML file there
    Return True if this was done, False if key.yaml already exists.
    """
    import stat
    # Expand the path if it contains '~'
    path = os.path.expanduser(config_path)
    if os.path.exists(path):
        return False
    # Check whether directory exists and create if necessary
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.mkdir(directory)
    # Set permissions to rw------- (700 in octal)
    os.chmod(directory, stat.S_IRUSR | stat.S_IWUSR | stat.S_IEXEC)
    sample_config = get_config(sample_config_path)
    write_config(path,sample_config)
    return True


