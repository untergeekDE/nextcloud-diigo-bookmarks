# nc_bookmarks_api.py

import os
import requests
import re


from config import *
from helpers import get_nc_key


def probe_bookmarks():
    response = requests.get(f"{nc_url}/index.php/apps/bookmarks/public/rest/v2/bookmark", auth=(nc_user,nc_key))
    if response.status_code == 200:
        bookmarks = response.json()
        print("Bookmarks probed successfully!")
        # Process the bookmarks data as needed
    else:
        print(f"Failed to reach bookmarks. Status code: {response.status_code}")

def create_bookmark(url, 
                    title="", 
                    description="", 
                    tags=[],
                    folders=[0]):
    bookmark_data = {
        "url": url,
        "title": title,
        "description": description,
        "tags": tags,
        "folders": folders
    }
    
    response = requests.post(f"{nc_url}/index.php/apps/bookmarks/public/rest/v2/bookmark",
                             headers= auth_headers,
                             json=bookmark_data,
                             auth=(nc_user, nc_key))
    
    if response.status_code == 200:
        j = response.json()
        if j['status'] == 'success':
            return j['item']['id']
        else:
            print("Could not create bookmark")
            return None
    else:
        print(f"Failed to create bookmark. Status code: {response.status_code}")

def edit_bookmark(id,data):
    bookmark_data = data
    
    response = requests.put(f"{nc_url}/index.php/apps/bookmarks/public/rest/v2/bookmark/{id}",
                             headers= auth_headers,
                             json=bookmark_data,
                             auth=(nc_user, nc_key))
    
    if response.status_code == 200:
        j = response.json()
        if j['status'] == 'success':
            return j['item']['id']
        else:
            print("Could not create bookmark")
            return None
    else:
        print(f"Failed to create bookmark. Status code: {response.status_code}")

# Return bookmark id for this url, None if not found
# TODO: What if multiple bookmarks are found? 

def find_bookmark(url,folder_id=-1):
    bookmark_data = {
        "url": url,
        "folder": folder_id,
    }
    response = requests.get(f"{nc_url}/index.php/apps/bookmarks/public/rest/v2/bookmark",
                            headers= auth_headers,
                            json=bookmark_data,
                            auth=(nc_user, nc_key))
    if response.status_code == 200:
        folders_j = response.json()
        if folders_j['status'] == "success":
            d = folders_j['data']
            return d
        else: # no success
            return None
    else:
        print(f"Failed to query bookmarks. Status code: {response.status_code}")
    return None

def check_bookmark(url):
    d = find_bookmark(url)
    if len(d)==1:
        return True
        
########### Folders ##############

# Dict of all folders in the root folder, with name and ID. 
def get_folders():   
    bookmark_data = {
        "root": -1
    }
    response = requests.get(f"{nc_url}/index.php/apps/bookmarks/public/rest/v2/folder",
                            headers= auth_headers,
                            json=bookmark_data,
                            auth=(nc_user, nc_key))
    if response.status_code == 200:
        folders_j = response.json()
        if folders_j['status'] == "success":
            return folders_j['data']
        else: # no success
            print("Failed to retrieve folders")
            return None
        return response.json()
    else:
        print(f"Failed to query folders. Status code: {response.status_code}")

def create_folder(name, parent =-1):   
    folder_data = {
        "title": name #,
        # "parent_folder": parent
    }
    response = requests.post(f"{nc_url}/index.php/apps/bookmarks/public/rest/v2/folder",
                            headers= auth_headers,
                            json=folder_data,
                            auth=(nc_user, nc_key))
    if response.status_code == 200:
        folders_j = response.json()
        if folders_j['status'] == "success":
            return folders_j['item']['id']
        else: # no success
            print(f"Failed to create folder {name} with parent {parent}")
            return None
        return response.json()
    else:
        print(f"Failed to create folders. Status code: {response.status_code}")


# Checks whether there is a folder with a name that matches the regex r,
# then return a list of all matching folder ids
def get_folder_id(r):
    f_j = get_folders()
    # f = []
    for j in f_j:
        if (r == j['title']):
        #if re.match(r,j['title']):
            return j['id']
    return None 
