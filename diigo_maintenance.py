# diigo_maintenance.py
#
# Code for manipulating Diigo API

import requests
import pandas as pd
from urllib.parse import quote
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from config import *
from helpers import get_nc_key
from import_csv import update_bookmarks
    

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

# This checks whether Diigo can be reached: 


def get_diigo_bookmarks(d_start = 0, d_count= 10, tags=""):
    d_params = {
        'key': quote(diigo_key),
        'user': quote(diigo_user)
    }
    # Add tags for filtering if tags string is given
    if tags != "":
        d_params['tags'] = tags
    if d_start >0: 
        d_params['start'] = d_start
    if d_count != 10: 
        d_params['count'] = d_count
    response = requests.get(f"{diigo_url}bookmarks",
                            params = d_params,
                            headers= auth_headers,
                            auth=(diigo_user, diigo_pw),
                            )
    if response.status_code == 200:
        bookmarks = response.json()
        return bookmarks
    else:
        print(f"Failed to reach bookmarks. Status code: {response.status_code}")
        print(f"API Message: {response.text}")
        return None

def probe_diigo_bookmarks():
    global diigo_key
    global diigo_pw
    diigo_key = get_nc_key(diigo_key_path)
    diigo_pw = get_nc_key(diigo_pw_path)
    r = get_diigo_bookmarks(d_start=0, d_count=1)
    if r != None: 
        print("OK - Can read Diigo bookmarks")
    else:
        raise Exception("Diigo bookmarks inaccessible")
    
def write_diigo_bookmark(title,url, # these are required, i.e. they ID the bookmark
                         shared=False,
                         tags="",
                         desc="",
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
    d_params = {
        'key': quote(diigo_key),
        'user': quote(diigo_user),
        'title': title,
        'url': url,
        'shared': "yes" if shared else "no",
        'tags': tags,
        'desc': desc,
        'readLater': f'{"yes" if readLater else "no"}',
        'merge': f'{"yes" if merge else "no"}',
    }
    response = requests.post(f"{diigo_url}bookmarks",
                            params = d_params,
                            headers= auth_headers,
                            auth=(diigo_user, diigo_pw),
                            )
    if response.status_code == 200:
        bookmarks = response.json()
        return True
    else:
        print(f"Failed to write bookmark '{title}' ({url}).\nStatus code: {response.status_code}")
        print(f"API Message: {response.text}")
        return None   

def delete_diigo_bookmark(title,url):
    # Experimental: Delete bookmark via API. The API description hints at it but does not
    # make this explicit. But it seems to work. 
    # YET: Bulk-deleting bookmarks seems to overload the database, 
    # getting a 400 error (internal server error) after some time.
    # In this case, wait and retry. 
    d_params = {
        'key': quote(diigo_key),
        'user': quote(diigo_user),
        'title': title,
        'url': url,
    }
    response = requests.delete(f"{diigo_url}bookmarks",
                            params = d_params,
                            headers= auth_headers,
                            auth=(diigo_user, diigo_pw),
                            )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to delete bookmark '{title}' ({url}).\nStatus code: {response.status_code}")
        print(f"API Message: {response.text}")
        return None    

### Functions using the interaction API of the website ### 

# Start a session and return a session cookie. 

# Returns a list of info. 
def get_diigo_info(page=0,sort='updated',count=24, session=None):
    # Experimental: get bookmark IDs
    # Set session cookie first by authenticating
    d_params = {
        'key': quote(diigo_key),
        'user': quote(diigo_user),
        'page_num': page,
        'sort': 'updated',
        'count': count,
    }
    if session != None: 
        response = session.get("https://www.diigo.com/interact_api/load_user_items",
                            headers = {
                                "Accept": "application/json", 
                                "Content-Type": "application/json",

                                "Authorization": "basic"
                                }, 
                            params = d_params,
                            auth=(diigo_user, diigo_pw),
                            )
    else:
        response = requests.get("https://www.diigo.com/interact_api/load_user_items",
                            headers = {
                                "Accept": "application/json", 
                                "Content-Type": "application/json",

                                "Authorization": "basic"
                                }, 
                            params = d_params,
                            auth=(diigo_user, diigo_pw),
                            )
    if response.status_code == 200:
        with open("./response.html", 'w') as f:
            f.write(response.text)
        return response.json()
    else:
        print(f"Failed to reach load_user_items.\nStatus code: {response.status_code}")
        print(f"API gives this reason: {response.text}")
        return None    


def delete_b_diigo_bookmark(title,url):
    # Experimental: Delete bookmark via API. The API description hints at it but does not
    # make this explicit. 
    # Not using the CURL DELETE method but rather a POST to the API
    # with a different verb 
    d_params = {
        'title': title,
        'url': url,
    }
    response = requests.post("https://www.diigo.com/interact_api/delete_b",
                            params = d_params,
                            headers= auth_headers,
                            auth=(diigo_user, diigo_pw),
                            )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to delete bookmark '{title}' ({url}).\nStatus code: {response.status_code}")
        return None    

def diigo_login():
    # Initialize the Selenium WebDriver (you may need to adjust this based on your browser)
    driver = webdriver.Firefox()  # Or webdriver.Firefox(), etc.
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
        selenium_cookies = driver.get_cookies()

        # Create a new requests session and add the cookies
        session = requests.Session()
        for cookie in selenium_cookies:
            session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])

        print("Login successful and session created.")
        return session
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    finally:
        # Close the browser
        driver.quit()


def test_diigo_api():
    # Just a brief test of the API; reading bookmarks, creating, overwriting, and deleting; 
    # filtering by tag does not seem to work though. 
    probe_diigo_bookmarks()
    # Print first 10 bookmarks
    print(get_diigo_bookmarks())
    # Write demo bookmark
    if write_diigo_bookmark(title="TEST",url="https://janeggers.tech",desc="foobar"):
        print("Success writing test bookmark")
    # Try overwriting it
    write_diigo_bookmark(title="TEST",url="https://janeggers.tech",desc="New Description",tags="nc_experimental")
    print(f"Overwritten bookmark: \n{get_diigo_bookmarks(tags='nc_experimental')}")
    # Start a session for the interaction API; login and authenticate
    session = diigo_login()
    test = get_diigo_info(session = session)
    print(test)
    # Cannot be found but the bookmark is there!
    # Try destroying it
    r = delete_b_diigo_bookmark(title="TEST", url="https://janeggers.tech")
    print(r)

if __name__ == "__main__":
    # First check if routine is already running (for CRON)
    # Look at file diigo.log and determin its age
    # If older than two minutes, go ahead
    # If done, rename log
    # Routine to download and destroy all bookmarks
    # 
    # Runs pretty well on my Raspi, killing away at those old
    # bookmarks. Bye, training data. 
    probe_diigo_bookmarks()
    test_diigo_api()
    print(f"Greetings. Downloading and destroying all Diigo bookmarks for user {diigo_user}")
    diigo_dump_path = "./diigo_dump.csv"
    print(f"Will create a file named '{diigo_dump_path}' with all bookmarks, then erase them via the API.")
    print("Proceeding in steps of 10 in case the procedure fails.")
    #    input("Proceed? Ctrl-C to abort, press return to start.")
    i = 0 
    step = 10
    d_b_dict = get_diigo_bookmarks(d_start=i, d_count=step)
    # Returns a json, i.e. a dict. 
    while len(d_b_dict) > 0:
        df = pd.DataFrame(d_b_dict)
        # Drop unwanted columns, keep only those in the list
        df = df[diigo_fields_list]
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