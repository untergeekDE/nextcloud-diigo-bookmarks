# nc_bookmarks_api.py

import requests
import pandas as pd

from config import *
from config_lib import get_nc_key

# Is there a Nextcloud at the URL?
def probe_nc_bookmarks_url(nc_url=None):
    if nc_url == None: 
        nc_url = config['nc_bookmarks']['nc_url']
    response = requests.get(nc_url)
    if response.status_code != 200: 
        # URL cannot be reached
        print (f"URL '{nc_url}' cannot be reached")
        return False
    # Look in response for title containing '– Nextcloud	'
    # We'll do this without BeautifulSoup.
    if '<title>' in response.text:
        title_start = response.text.index('<title>') + 7
        title_end = response.text.index('</title>', title_start)
        title = response.text[title_start:title_end]
        if '– Nextcloud' in title:
            print(f"Nextcloud instance found at '{nc_url}'")
            return True
        else:
            print(f"No Nextcloud instance found at '{nc_url}'")
            return False
    else:
        print(f"No title tag found in the response from '{nc_url}'")
        return False

# Test whether API can be reached. 
# 
# Needs user and password in config dictionary
def probe_nc_bookmarks():
    if config['nc_bookmarks']['user'] + config['nc_bookmarks']['password'] == "":
        print("nc_bookmarks user/password not set")
        return False
    response = requests.get(f"{nc_url}/index.php/apps/bookmarks/public/rest/v2/bookmark", 
                            auth=(config['nc_bookmarks']['user'],config['nc_bookmarks']['password']))
    if response.status_code == 200:
        bookmarks = response.json()
        print("Bookmarks probed successfully!")
        # Process the bookmarks data as needed
        return True
    else:
        print(f"Failed to reach bookmarks. Status code: {response.status_code}")
        return False

def create_nc_bookmark(url, 
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
    
    response = requests.post(f"{config['nc_bookmarks']['nc_url']}/index.php/apps/bookmarks/public/rest/v2/bookmark",
                             headers= auth_headers,
                             json=bookmark_data,
                             auth=(config['nc_bookmarks']['user'],config['nc_bookmarks']['password']))
    
    if response.status_code == 200:
        j = response.json()
        if j['status'] == 'success':
            return j['item']['id']
        else:
            print("Could not create bookmark")
            return None
    else:
        print(f"Failed to create bookmark. Status code: {response.status_code}")

# Update bookmark with given ID.
# If no ID is given, create from scratch. (NC Bookmarks might overwrite existing bookmarks.)
def edit_nc_bookmark(data,id=None):
    bookmark_data = data
    api_url = f"{config['nc_bookmarks']['nc_url']}/index.php/apps/bookmarks/public/rest/v2/bookmark"
    # Is there an ID? If yes, add to API call. 
    if id != None:
        api_url += f"/{id}"
    response = requests.put(api_url,
                             headers= auth_headers,
                             json=bookmark_data,
                             auth=(config['nc_bookmarks']['user'],config['nc_bookmarks']['password']))
    
    if response.status_code == 200:
        j = response.json()
        if j['status'] == 'success':
            return j['item']['id']
        else:
            print("Could not create bookmark")
            return None
    else:
        print(f"Failed to create bookmark. Status code: {response.status_code}")

# Retrieve a list of bookmarks from the given folder, selected by the given tags and filter word
def get_nc_bookmarks(page = 0,
                     limit = 10,
                     tags = [],
                     sortby = 'lastmodified',
                     search = [],
                     conjunction = 'or',
                     folder = None,
                     url = None
):
    """
    - page (int, default 0; pagination unit is limit)
    - limit (int, default 10 - the number of hits)
    - tags (list, default []) – 
    - sortby (['url', 'title', 'description', 'public', 
            'lastmodified', 'clickcount'], default: 'lastmodified')
    - search ([], words to filter by)
    - conjunction (['and','or'], default: 'or')
    - folder (int)
    - url (which is ignored here; use "find_nc_bookmarks")

    Returns a list of dicts containing the bookmarks - with ID!
    """
    global config
    bookmark_data = {
        'page': page,
        'limit': limit,
        'tags': tags,
        'sortby': 'lastmodified',
        'search': [],
        'conjunction': 'or',
    }
    if folder != None: 
        bookmark_data['folder'] = folder
    # Ignore URL for the time being. 
    response = requests.get(f"{config['nc_bookmarks']['nc_url']}/index.php/apps/bookmarks/public/rest/v2/bookmark",
                            headers= auth_headers,
                            json=bookmark_data,
                            auth=(config['nc_bookmarks']['user'],
                                  config['nc_bookmarks']['password']))
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

# Return bookmark id for this url, None if not found
def find_nc_bookmark(url,folder_id=-1):
    global config
    bookmark_data = {
        "url": url,
        "folder": folder_id,
    }
    response = requests.get(f"{config['nc_bookmarks']['nc_url']}/index.php/apps/bookmarks/public/rest/v2/bookmark",
                            headers= auth_headers,
                            json=bookmark_data,
                            auth=(config['nc_bookmarks']['user'],
                                  config['nc_bookmarks']['password']))
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

def check_nc_bookmark(url):
    d = find_nc_bookmark(url)
    return len(d)==1


def get_nc_dump():
    df = pd.DataFrame()
    p = 0
    nc_batch_size = config['nc_batch_size']
    data = get_nc_bookmarks(page = 0, limit = nc_batch_size)
    while len(data) > 0: 
        b_df = pd.DataFrame(data)
        df =  pd.concat([df, b_df], ignore_index=True)   
        p += 1
        data = get_nc_bookmarks(page = 0, limit = nc_batch_size)
    return df


########### Folders ##############

# Dict of all folders in the root folder, with name and ID. 
def get_nc_folders():   
    global config
    bookmark_data = {
        "root": -1
    }
    response = requests.get(f"{config['nc_bookmarks']['nc_url']}/index.php/apps/bookmarks/public/rest/v2/folder",
                            headers= auth_headers,
                            json=bookmark_data,
                            auth=(config['nc_bookmarks']['user'],
                                  config['nc_bookmarks']['password']))
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

def create_nc_folder(name, parent =-1):  
    global config 
    folder_data = {
        "title": name #,
        # "parent_folder": parent
    }
    response = requests.post(f"{config['nc_bookmarks']['nc_url']}/index.php/apps/bookmarks/public/rest/v2/folder",
                            headers= auth_headers,
                            json=folder_data,
                            auth=(config['nc_bookmarks']['user'],
                                  config['nc_bookmarks']['password']))
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
def get_nc_folder_id(r):
    f_j = get_nc_folders()
    # f = []
    for j in f_j:
        if (r == j['title']):
        #if re.match(r,j['title']):
            return j['id']
    return None 

def get_nc_folder(name):
# Is there already a folder called name?
    folder_id = get_nc_folder_id(name)
    if folder_id == None:
        print(f"Creating Nextcloud folder {name}...")
        folder_id = create_nc_folder(name)
        if folder_id == None:
            raise Exception(f"Could not create {name} folder")
    else:
        return(folder_id)

def get_nc_diigo_folder():
    return get_nc_folder("DIIGO")