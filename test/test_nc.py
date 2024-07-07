############ OBSOLETE ##############
# 
# Very first test to reach the Nextcloud via the API,
# using a dedicated package rather than simple requests calls


# Kurzer Test der Nextcloud-API
#
# Nutze App-Login

from nc_py_api import Nextcloud
import os

def get_nc_key(path):
    path = os.path.expanduser(path)
    if os.path.exists(path):
        with open(path, "r") as file:
            nc_pass = file.read().strip()
            return nc_pass
    else:
        raise Error(f"Key-Datei {path} nicht gefunden")

nc_url = "https://www.eggers-elektronik.de/nextcloud/"
nc_path = "~/key/nc.key"
nc_user = "Jan"


def list_dir(directory):
    # usual recursive traversing over directories
    for node in nc.files.listdir(directory):
        if node.is_dir:
            list_dir(node)
        else:
            print(f"{node.user_path}")

if __name__ == "__main__":
    nc_pass = get_nc_key(nc_path)
    nc = Nextcloud(nextcloud_url=nc_url, nc_auth_user=nc_user, nc_auth_pass=nc_pass)
    # list_dir("/")
    all_files_folders = nc.files.listdir(depth=3)
    for obj in all_files_folders:
        print(obj.user_path)
