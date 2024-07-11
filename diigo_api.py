# diigo_maintenance.py
#
# Code for manipulating Diigo API

import requests
import json
import pandas as pd
from urllib.parse import quote
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from http.client import HTTPConnection


from config import *
from import_export import update_bookmarks, move_backup, inspect_file
from process import refactor_diigo_bookmark, suggest_description, suggest_tags
from nc_bookmarks_api import edit_nc_bookmark, get_nc_folder
    

# Sample API call: https://secure.diigo.com/api/v2/bookmarks?key=your_api_key&user=joel&count=10
# 
# Get via requests library
#
# The Diigo API is rather incomplete. Took me a while to realize that it expects you to send
# username, user password (in the HTTP authentification) AND the api key. 
# The API key has to be generated on Diigo first. 
# Documentation (it's not much): https://www.diigo.com/api_dev
#
# Props for this forgotten repository which made me realize the auth method: 
# https://github.com/chriskyfung/Evernote-ENEX-to-Diigo-Bookmarks
#
# Probably also valid (undocumented) API calls: 
# - load_user_items
# - load_shared_to_groups
# - load_user_info
# - load_user_tags&type=all
# - POST/delete_b

# This checks whether the Diigo API can be reached.
# Needs valid user, password, apikey in the config to work. 

def check_credentials_missing():
    if config['diigo']['user'] == None:
        print("config.yaml not read")
        return True
    if config['diigo']['user'] == "": 
        print("No User")
        return True
    if config['diigo']['apikey'] == "":
        print("No API key")
        return True
    return False

##############################################################
# Routines using the official API (as documented in https://www.diigo.com/api_dev)

# Get a chronological list of bookmarks, returned as a list of dicts
def get_diigo_bookmarks(d_start = 0, d_count= 10, tags=""):
    if check_credentials_missing():
        return None
    d_params = {
        'key': quote(config['diigo']['apikey']),
        'user': quote(config['diigo']['user'])
    }
    # Add tags for filtering if tags string is given
    if tags != "":
        d_params['tags'] = tags
    if d_start >0: 
        d_params['start'] = d_start
    if d_count != 10: 
        d_params['count'] = d_count
    response = requests.get("https://secure.diigo.com/api/v2/bookmarks",
                            params = d_params,
                            headers= AUTH_HEADERS,
                            auth=(config['diigo']['user'], config['diigo']['password']),
                            )
    if response.status_code == 200:
        bookmarks = response.json()
        return bookmarks
    else:
        print(f"Failed to reach bookmarks. Status code: {response.status_code}")
        print(f"API Message: {response.text}")
        return None

# Check whether API can be reached, and credentials are valid.
def probe_diigo_api():
    if check_credentials_missing():
        return None
    r = get_diigo_bookmarks(d_start=0, d_count=1)
    if r != None: 
        print("OK - Can read Diigo bookmarks")
        return True
    else:
        raise Exception("Diigo bookmarks inaccessible")
        return False

# Creates/overwrite a bookmark identified by URL and title
def write_diigo_bookmark(title,url, # these are required, i.e. they ID the bookmark
                         shared=False,
                         tags="",
                         description="",
                         readLater=False,
                         merge=False):
    """
    Bookmark is IDd by title and url strings. Other parameters are optional:
    - shared: Public or private bookmark?
    - tags: String contains comma-separated list of tags
    - desc: String contains description
    - readLater: Marked as saved for later reading
    - merge: If yes, do not overwrite existing bookmark but append
    """
    if check_credentials_missing():
        return None
    d_params = {
        'key': quote(config['diigo']['apikey']),
        'user': quote(config['diigo']['user']),
        'title': title,
        'url': url,
        'shared': "yes" if shared else "no",
        'tags': tags,
        'desc': description,
        'readLater': f'{"yes" if readLater else "no"}',
        'merge': f'{"yes" if merge else "no"}',
    }
    response = requests.post("https://secure.diigo.com/api/v2/bookmarks",
                            params = d_params,
                            headers= AUTH_HEADERS,
                            auth=(config['diigo']['user'], config['diigo']['password']),
                            )
    if response.status_code == 200:
        bookmarks = response.json()
        return True
    else:
        print(f"Failed to write bookmark '{title}' ({url}).\nStatus code: {response.status_code}")
        print(f"API Message: {response.text}")
        return None   

# Delete a bookmark identified by URL and title. 
#
# The session parameter is actually a bit of superstition: I strongly believe that
# the rate limit for the delete function is less severe if you are on a valid Diigo browser session.
# 

def delete_diigo_bookmark(title,url,session = None):
    # Experimental: Delete bookmark via API. The API description hints at it but does not
    # make this explicit. But it seems to work. 
    # YET: This method is rate-limited to some couple of dozen calls per ten minutes.
    # And: deleting bookmarks in rapid succession seems to overload the database, 
    # getting a 400 error (internal server error) after some time.
    # In this case, wait and retry. 
    if check_credentials_missing():
        return None
    diigo_user = config['diigo']['user']
    diigo_password = config['diigo']['password']
    diigo_apikey = config['diigo']['apikey']
    d_params = {
        'user': diigo_user,
        'key': diigo_apikey,
        'title': title,
        'url': url,
    }
    if session == None: 
        response = requests.delete("https://secure.diigo.com/api/v2/bookmarksbookmarks",
                                params = d_params,
                                headers= AUTH_HEADERS,
                                auth=(diigo_user,diigo_password),
                                )
    else: 
        response = session.delete("https://secure.diigo.com/api/v2/bookmarks",
                                  params = d_params,
                                  headers = AUTH_HEADERS,
                                  auth = (diigo_user,diigo_password))
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to delete bookmark '{title}' ({url}).\nStatus code: {response.status_code}")
        print(f"API Message: {response.text}")
        return None    

#################################################
### Functions using the Diigo Interaction API ###

# This is what is being used on the Diigo website; it needs you 
# to authenticate to your account to work. 
# I'll call it "dia" from here on. 

# Checks whether dia can be reached. 
# Actually needs a session to work, so call this only from a 
# valid requests session (otherwise it will return False) 
def probe_dia(session):
    global config
    # apikey = config['diigo']['apikey']
    user = config['diigo']['user']    
    password = config['diigo']['password']
    response = session.get("https://www.diigo.com/interact_api/load_user_items",
                            headers = AUTH_HEADERS,
                            params = {'page_num':0,
                                      'count':1},
                            auth=(user, password),
                            )
    if response.status_code == 200:
        try: 
            j = json.loads(response.text)
            return True
        except:
            # response.text seems to be no JSON - no login
            return False
    else:
        print("Unable to reach Diigo Interaction API")
        print(f"{response.status_code} - {response.text}")
        return False

# Get session cookies to use, either from disk, or from a browser session 
def dia_session_authenticate():
    # Initialize the Selenium WebDriver (you may need to adjust this based on your browser)
    try:
        driver = webdriver.Firefox()  # Or webdriver.Firefox(), etc.
    except:
        try:
            driver = webdriver.Chrome()
        except:
            raise("Could not initiate Selenium driver for Firefox or Chrome")
    try:
        # Navigate to the Diigo login page
        driver.get('https://www.diigo.com/sign-in')
    
        # Wait for the user to manually log in
        print("Please log in to Diigo in the opened browser window.")
        print("Once you've successfully logged in, the script will continue.")

        # Wait for the user to be redirected to the dashboard or home page after login
        WebDriverWait(driver, 300).until(
            EC.url_contains('https://www.diigo.com/user/')
        )

        # Get the cookies from the authenticated session
        session_cookies = driver.get_cookies()
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    finally:
        # Close the browser
        driver.quit()   
    write_config(SESSION_PATH,session_cookies)
    return session_cookies
                            
# Check where a session_cookies.yaml file can be found and used. 
# If that does not work, i.e. returns HTML instead of JSON,
# or the force_reauth parameter is set: 
# Open a browser, have the user log in, and retrieve the session cookies.
# Save them to a session_cookies.yaml file, open a requests session with
# the newfound cookies, and save them. 
def dia_login(force_reauth = False): 
    global config
    config = get_config(CONFIG_PATH)
    # Enable debugging at HTTPConnection level
    if LOG == 1: 
        HTTPConnection.debuglevel = 1
        # Set up logging
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

    if not force_reauth:
        session_cookies = get_yaml(SESSION_PATH)
        if session_cookies != None:
            # Read session cookies successfully, start
            # requests session, and try to probe it
            session = requests.Session()
            for cookie in session_cookies:
                session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])
            # Create a new requests session and add the cookies
            if probe_dia(session):
                # Successful login
                return session
    # Seems to have failed, continue and reauth.  
    session_cookies = dia_session_authenticate()
    # So on ideal terms, we have a valid session saved now.
    session = requests.Session()
    for cookie in session_cookies:
        session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])
    # Create a new requests session and add the cookies
    if probe_dia(session=session):
        # Successful login
        return session
    session.close()
    print("Failed to authenticate")
    return None
   
# Returns a paginated list of bookmarks 
# Pagination is determined by the page_num and count parameters: 
# page_num=0, count=10 gives you bookmarks 1-10, page_num=2, count=20 gives you 41-60. 
def dia_load_user_items(page_num=0,sort='updated',count=24, session=None):
    # Set session cookie first by authenticating
    global config
    diigo_key = config['diigo']['apikey']
    diigo_user = config['diigo']['user']
    diigo_password = config['diigo']['password']
    d_params = {
        'page_num': page_num,
        'sort': 'updated',
        'count': count,
    }
    if session != None: 
        response = session.get("https://www.diigo.com/interact_api/load_user_items",
                            headers = AUTH_HEADERS, 
                            params = d_params,
                            auth=(diigo_user, diigo_password),
                            )
    else:
        print("No session")
        return None
    if response.status_code == 200:
        try:
            j = response.json()
            return j['items']
        except:
            print("Failed to return JSON - probably no longer authenticated")
            return None
    else:
        print(f"Failed to reach load_user_items.\nStatus code: {response.status_code}")
        print(f"API gives this reason: {response.text}")
        return None    

# Returns a paginated list of bookmarks, filtered by "what" parameter 
# Basically the same as dia_load_user_items.
# Pagination is determined by the page_num and count parameters: 
# page_num=0, count=10 gives you bookmarks 1-10, page_num=2, count=20 gives you 41-60. 
def dia_search_user_items(what="",page_num=0,sort='updated',count=24, session=None):
    # Set session cookie first by authenticating
    global config
    diigo_key = config['diigo']['apikey']
    diigo_user = config['diigo']['user']
    diigo_password = config['diigo']['password']
    d_params = {
        'what': what,
        'page_num': page_num,
        'sort': 'updated',
        'count': count,
    }
    if session != None: 
        response = session.get("https://www.diigo.com/interact_api/search_user_items",
                            headers = AUTH_HEADERS, 
                            params = d_params,
                            auth=(diigo_user, diigo_password),
                            )
    else:
        print("No session")
        return None
    if response.status_code == 200:
        try:
            j = response.json()
            return j['items']
        except:
            print("Failed to return JSON - probably no longer authenticated")
            return None
    else:
        print(f"Failed to reach load_user_items.\nStatus code: {response.status_code}")
        print(f"API gives this reason: {response.text}")
        return None    

def dia_get_id(page_num=0,sort='updated',count=24, session=None, what=""):
    # Return a list of numerical IDs
    if what != "":
        items = dia_search_user_items(page_num=page_num,sort=sort,count=count,session=session,what=what)
    else:
        items = dia_search_user_items(page_num=page_num,sort=sort,count=count,session=session)
    id_list = [i['link_id'] for i in items]
    return id_list

# Write, or overwrite, bookmark
def dia_write(title,
              url, 
              description="",
              new_url = "",
              private = "",
              unread = "",
              link_id=None,
              session=None):
    # Kill all bookmarks in the list (which may be either a real list,
    # or a string containing comma-separated values)
    diigo_user = config['diigo']['user']
    diigo_password = config['diigo']['password']
    if type(link_id) == list: 
        link_id = ','.join(map(str, link_id))
    d_params = {
        'url': url,
    }
    if link_id != None:
        d_params['link_id'] = link_id
    if title != "":
        d_params['title'] = title
    if description != "":
        d_params['description'] = description
    if new_url != "":
        d_params['new_url'] = new_url
    if private != "":
        d_params['private'] = private
    if unread != "":
        d_params['unread'] = unread
    d_headers = AUTH_HEADERS
    d_headers['Origin'] = 'https://www.diigo.com'
    d_headers['Referer'] = f'https://www.diigo.com/user/{diigo_user}?query=test'

    if session != None: 
        response = session.post("https://www.diigo.com/item/save/bookmark",
                            params = d_params,
                            headers= d_headers,
                            auth=(diigo_user,diigo_password),
                            )
    else:
        print("No Session")
        return None
    if response.status_code == 200:
        """ Although the call returns a non-JSON, it seems to work OK. 
        try:
            j = json.loads(response.text)
            return j
        except:
            # Presumably, no json return value
            print("Returned non-JSON value; wrong parameters?")
            return None
        """
        return True
    else:
        print(f"Failed to reach load_user_items.\nStatus code: {response.status_code}")
        print(f"API gives this reason: {response.text}")
        return None 

############################################################
# Bulk API

# These function calls to manipulate bookmarks in bulk... they don't work. 
# You can see them working on the Diigo site, but they only return a 403 Forbidden
# status, and my guess is that they are only valid for calls from diigo.com. Bummer.

# Bulk-change visibility of bookmarks
#
# The 'silent' parameter is used to suppress printing error messages and warnings
def dia_change_mode_b(link_id, mode=2, session=None, silent = False):
    # Kill all bookmarks in the list (which may be either a real list,
    # or a string containing comma-separated values)
    diigo_user = config['diigo']['user']
    diigo_password = config['diigo']['password']
    if type(link_id) == list: 
        link_id = ','.join(map(str, link_id))
    d_params = {
        'link_id': link_id,
        'mode': mode
    }
    # Try to augment headers
    d_headers = AUTH_HEADERS
#    d_headers['Origin'] = 'https://www.diigo.com'
#    d_headers['Referer'] = f'https://www.diigo.com/user/{diigo_user}?query=test'
    if session != None: 
        response = session.post("https://www.diigo.com/ditem_mana2/convert_mode",
                            params = d_params,
                            headers= d_headers,
                            auth=(diigo_user, diigo_password),
                            )
    else:
        if not silent:
            print("No Session")
            return None
    if response.status_code == 200:
        try:
            j = json.loads(response.text)
            return j
        except:
            # Presumably, no json return value
            if not silent:
                print("Returned non-JSON value; wrong parameters?")
            return response.status_code
    else:
        if not silent:
            print(f"Failed to execute change_mode_b.\nStatus code: {response.status_code}")
            print(f"API gives this reason: {response.text}")
        return response.status_code   

# Bulk-delete a list of bookmarks
def dia_delete_b(link_id, session=None):
    # Kill all bookmarks in the list (which may be either a real list,
    # or a string containing comma-separated values)
    diigo_user = config['diigo']['user']
    diigo_password = config['diigo']['password']
    if type(link_id) == list: 
        link_id = ','.join(map(str, link_id))
    d_params = {
        'link_id': link_id
    }
    # Try to augment headers
    d_headers = AUTH_HEADERS
    d_headers['Origin'] = 'https://www.diigo.com'
    d_headers['Referer'] = f'https://www.diigo.com/user/{diigo_user}?query=test'
    if session != None: 
        response = session.post("https://www.diigo.com/ditem_mana2/delete_b",
                            params = d_params,
                            headers= d_headers,
                            auth=(diigo_user, diigo_password),
                            )
    else:
        print("No Session")
        return None
    if response.status_code == 200:
        try:
            j = json.loads(response.text)
            return j
        except:
            # Presumably, no json return value
            print("Returned non-JSON value; wrong parameters?")
            return None
    else:
        print(f"Failed to execute delete_b.\nStatus code: {response.status_code}")
        print(f"API gives this reason: {response.text}")
        return response.status_code   

###################################################################################
########## Test both APIs by writing, overwriting, listing, deleting bookmark #####

def test_diigo_api(diigo_api = True, dia_api = True):
    # Just a brief test of the API; reading bookmarks, creating, overwriting, and deleting; 
    # filtering by tag does not seem to work though. 
    global config
    print("Getting credentials from disk")
    config = get_config(CONFIG_PATH)
    if diigo_api:    
        print(get_diigo_bookmarks())
        # Write demo bookmark using the regular API
        if write_diigo_bookmark(title="TEST",url="https://janeggers.tech",description="foobar"):
            print("Success writing test bookmark")
        # Try overwriting it
        write_diigo_bookmark(title="TEST",url="https://janeggers.tech",description="New Description",tags="nc_experimental")
        print(f"Overwritten bookmark: \n{get_diigo_bookmarks(tags='nc_experimental')}")
        r = delete_diigo_bookmark(title="TEST", url="https://janeggers.tech")
        print(r)
    if dia_api:
        # Start a session for the interaction API; login and authenticate
        session = dia_login()
        test = dia_load_user_items(session = session)
        if len(test) > 0:
            print("Found first: ", test[0]['url'],test[0]['title'])
        else:
            print("No bookmarks found")
        #       test = dia_delete_b("749192573", session = session)
        print("Creating bookmark test07")
        dia_write(title="Test07", url="https://untergeek.de/test", description = "A test.", session=session)
        test = dia_search_user_items(what="test",session = session)
        print("Found first: ", test[0]['url'],test[0]['title'],"with ID",test[0]['link_id'])

        print("Trying update: retrieving link_id")
        hit_list = dia_get_id(what="test07", session = session)
        dia_write(title="Nomnomnom", url="https://janeggers.tech", link_id=hit_list, session=session)
        print("Updated bookmark",hit_list)
        if dia_delete_b(hit_list,session=session) == 403:
            print("dia_delete_b refused deletion, trying API delete")
            response = delete_diigo_bookmark(title="Nomnomnom", url="https://janeggers.tech",session=session)
            print(response)
        else: 
            print("Deleted test bookmark")
        session.close()
    
### Make private, export, recreate, and remove bookmarks via Interaction API

# Set all bookmarks to private
def dia_privatize():
    # Login
    session = dia_login()
    p = 0
    n = 0
    diigo_batch_size = config['diigo_batch_size']
    # Step through Diigo bookmarks in batches of diigo_batch_size = 100.
    print(f"Processing in batches of {diigo_batch_size}") 
    print("Batch progress: (.) Reading (-) Changing (*) Done")
    items = dia_load_user_items(page_num=p,
                                sort = 'created_at',
                                count= diigo_batch_size,    # defined in config.py
                                session = session)
    while len(items) > 0:
        print(".",end = "")
        # If existing bookmark file is found, move to .bak
        # Tends to contain empty lists; convert these to strings        
        # Overwrite bookmarks as private
        """ OBSOLETE: Overwrite each single bookmark - far too slow
        """
        # Bulk-change 
        list_id = [i['link_id'] for i in items]
        response = dia_change_mode_b(list_id,mode="2",session=session,silent=True)
        if response == 403:
            # Seems like we cannot bulk-delete from another IP; go for slow but reliable:
            # Overwrite every single bookmark
            for i in items:
                print("\b-",end="")
                response = dia_write(title=i['title'],
                                        url=i['url'],
                                        link_id=i['link_id'],
                                        private="true",
                                        session=session)
                if response:
                    print("\b.",end="")
                    n+=1
            else:
                n += p
        print("\b*")
        p+=1
    print(f"Set {n} bookmarks to private")
    session.close()    
    return True

# 
def dia_export_delete(create_nextcloud = False,
                      remove_diigo = False,
                      use_llm = False):
    # Get ID of DIIGO folder on Nextcloud (or create if not there)
    if create_nextcloud: 
        diigo_folder = get_nc_folder(DIIGO_FOLDER)
        unread_folder = get_nc_folder(UNREAD_FOLDER)
        private_folder = get_nc_folder(PRIVATE_FOLDER)
        unreachable_folder = get_nc_folder(UNREACHABLE_FOLDER)
    # Login
    session = dia_login()
    move_backup(config['diigo_dump_path'])
    p = 0
    diigo_batch_size = config['diigo_batch_size']
    # Step through Diigo bookmarks in batches of diigo_batch_size = 100.
    print(f"Processing in batches of {diigo_batch_size}") 
    print(f"Batch progress: (.) Reading (v) Dumping {'(@) AI reflecting ' if use_llm else ''}{'(X) Removing' if remove_diigo else ''} (*) Done")
    print(".",end="")
    items = dia_load_user_items(page_num=p,
                                sort = 'created_at',
                                count= diigo_batch_size,    # defined in config.py
                                session = session)
    while len(items) > 0:
        print("\bv",end = "")
        # Add to CSV
        df = pd.DataFrame(items)
        # If existing bookmark file is found, move to .bak
        # Tends to contain empty lists; convert these to strings        
        update_bookmarks(config['diigo_dump_path'],df)

        # Create Nextcloud Bookmarks if necessary here
        if create_nextcloud: 
            for i in items:
                print("\b^",end="")
                folders = [diigo_folder] 
                if i['readed'] == 0:
                    folders.append(unread_folder)
                if not i['private']: # Yes, it's private if False!
                    folders.append(private_folder)
                bookmark_data = refactor_diigo_bookmark(url = i['url'],
                                                        title = i['title'],
                                                        description = i['description'],
                                                        annotations = i['annotations'],
                                                        comments = 'comments',
                                                        created_at = i['created_at']
                                                        )
                # Assign folders to NC bookmark
                bookmark_data['folders'] = folders
                # create bookmark
                # Use LLM
                if use_llm:
                    print("\b@",end="")                 
                    llm_d = suggest_description(bookmark_data['url'],
                                                bookmark_data['description'])
                    if llm_d == None: 
                        folders.append(unreachable_folder)
                    else:
                        bookmark_data['description'] = bookmark_data['description'].replace('###LLM###', llm_d)
                    # TODO: Add tagging
                edit_nc_bookmark(bookmark_data)
                print("\b*",end="")
                

        # Bulk-delete bookmarks in list
        if remove_diigo: 
            print("\bX",end="")
            id_list = [i['link_id'] for i in items]
            response = dia_delete_b(id_list, session = session)
            if response == 403:
                print(f"dia_delete_bookmarks returned 'Forbidden', could not delete those: {id_list}")
                for i in items:
                    title = i['title']
                    url = i['url']
                    print(f"Trying force-delete {url} {title}")
                    response = delete_diigo_bookmark(title=title,url=url,session = session)
                    print(f"Response: {response}")
                    while (response == None):
                        print("Waiting 5 minutes for retry")
                        time.sleep(300)
                        response = delete_diigo_bookmark(title=title,url=url,session = session)
                    
                    # Wait 2 seconds 
                    time.sleep(2)
            
        else: 
            # No bookmarks have been removed, so we have to go to the next page. 
            p += 1 
        # Load next batch
        print("\b*.",end="")
        items = dia_load_user_items(page_num=p,
                                    sort = 'created_at',
                                    count=diigo_batch_size,
                                    session = session)
    # Erase the last read symbol and erase
    print("\b \n")     
    session.close()
    df = inspect_file(config['diigo_dump_path'])
    # Shows file and waits for ENTER
    

### Export and remove bookmarks via official API (SLOW) ### 

def diigo_export_delete(): 
    # Runs, sort of. Rate limit after some deletions, so it may take time. 
    probe_diigo_api()
    # probe_dia()
    print(f"Greetings. Downloading and destroying all Diigo bookmarks for user {config['diigo']['user']}")
    diigo_dump_path = config['diigo_dump_path'] # "../data/diigo_dump.csv"
    print(f"Will create a file named '{config['diigo_dump_path']}' with all bookmarks, then erase them via the API.")
    print("Proceeding in steps of 10 in case the procedure fails.")
    #    input("Proceed? Ctrl-C to abort, press return to start.")
    i = 0 
    step = 10
    d_b_dict = get_diigo_bookmarks(d_start=i, d_count=step)
    # Returns a json, i.e. a dict. 
    while len(d_b_dict) > 0:
        df = pd.DataFrame(d_b_dict)
        # Drop unwanted columns, keep only those in the list
        df = df[DIIGO_FIELDS_LIST]
        # Tends to contain empty lists; convert these to strings
        df = df.apply(lambda col: col.apply(lambda x: '' if isinstance(x, list) else x))

        update_bookmarks(diigo_dump_path,df)
        for bookmark in d_b_dict:
            url = bookmark['url']
            title = bookmark['title']
            # Kill it
            if delete_diigo_bookmark(title=title, url=url)!= None:
                print(f"Removed {url}, waiting...")
                time.sleep(1)
            else:
                print("Waiting a literal minute...")
                get_diigo_bookmarks()
                time.sleep(60)
                if delete_diigo_bookmark(title=title, url = url) != None:
                    print("Success on the 2nd attempt.")
                else:
                    print("Still won't work. Retrying on the next round...")
        df = pd.DataFrame()  # Reset the DataFrame
        i += 10
        # I had a logical error in here. If I remove bookmarks, 
        # I must of course start from 0, not from i
        # (as former bookmarks 0-9 have been removed).
        #  
        d_b_dict = get_diigo_bookmarks(d_start=0, d_count=step)
        while d_b_dict == None:
            # Why is this? Those recurring delay calls seem to
            # overload the Diigo server. After a few dozen 
            # calls, it responds with a 400 Internal Error.
            #
            # Waiting and retrying generally helps. 
            # 
            # Yet, after some time, the server gives a 400
            # even when trying to read bookmarks, and this is
            # when you have to wait a couple of minutes. 
            #
            # And no, adding some waiting time after each 
            # delete action did not help. And I did not find
            # any provisions for bulk-deleting (yet?)
            print("Cannot reach Diigo - I'll be back in five.")
            time.sleep(300)
            d_b_dict = get_diigo_bookmarks(d_start=0, d_count=step)
            

    print(f"Done. Exported and removed {i+len(d_b_dict)} bookmarks.")

if __name__ == "__main__":
    test_diigo_api(diigo_api=False, dia_api=True)