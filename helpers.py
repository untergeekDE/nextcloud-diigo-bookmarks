# helpers.py

from datetime import datetime
import os

# Convert Unix time to datetime object
# unix_time = 1684915200  # Example Unix time
# datetime_obj = datetime.fromtimestamp(unix_time)

# print("Unix time:", unix_time)
# print("Datetime object:", datetime_obj)


def get_nc_key(path):
    path = os.path.expanduser(path)
    if os.path.exists(path):
        with open(path, "r") as file:
            nc_pass = file.read().strip()
            return nc_pass
    else:
        raise FileNotFoundError(f"Key file {path} not found")