Code and format documentation as part of the [nextcloud-bookmarks](README.md) repository

# Documentation

Overview on what the code does where. 

## Libraries and functions

- **main.py** gives you the menu that calls functions for diigo and nextcloud - the main routine
- **config.py** contains global parameters, settings, and prompts

- **config_lib.py** contains routines for reading and writing the YAML files that contain user credits and session cookies
- **diigo_api.py** contains functions for talking to Diigo. Called with ```python diigo_api.py```, the script performs a test of the API by writing, retrieving, and deleting a bookmark via both the official API and the interaction API. 
- **file_menu.py** is a subroutine for a text-based file selector menu. Called with ```python file_menu.py```, a demo routine for selecting and displaying a .txt file is performed.
- **import_csv.py** contains functions to read and write CSVs containing bookmarks, and moving them to a backup, and displaying them
- **nc_bookmarks_api.py** contains functions for reading and manipulating Nextcloud bookmarks and folders
- **nc_llm_improve** is, as of now, empty - it is supposed to contain a stand-alone routine to look at the bookmarks in a Nextcloud installation, and improve descriptions and bookmarks with an AI language model. 
- **process.py** contains routines to process tags and descriptions. AI prompting to suggest descriptions and tags happens here, as well as basic stuff like counting tags, and selecting the better of two descriptions (easy: pick the longer one).
- **upload_bookmarks.py** is a legacy standalone routine to upload a CSV with Diigo bookmarks to Nextcloud. 

### ```config.py``` - Global parameters, settings and prompts

Most of the settings for the code are kept in a global dict variable named ```config```, which is read from a config.yaml file from disk. The config.py file hard-codes settings not in the config.yaml file.

- VERSION_STRING = "nextcloud-diigo-bookmarks V0.4.1 alpha"
- LOG = 0 (set to 1 to log diigo API requests to the console for debugging)
- diigo_url = "https://secure.diigo.com/api/v2/"
- config_path = "~/.ncdbookmarks/config.yaml" (Location of config file)
- sample_config_path = "./sample_config.yaml" (Location of sample config file)
- session_path = "~/.ncdbookmarks/session_cookies.yaml" (location of session cookies file)

- b_path (hard-coded path to a bookmarks CSV to upload in upload_bookmarks.py)
- tags_path (hard-coded path to save tags)

Folder names: 
- DIIGO_FOLDER = "DIIGO"
- UNREAD_FOLDER = "LESEN"
- PRIVATE_FOLDER = "PRIVAT"
- UNREACHABLE_FOLDER = "Abgelaufen"
- UNIQUE_TAG_FOLDER = "EinzelfallTags" (tags that have been used only once)

Prompts:
- summarize_en_p (prompt for summarizing websites in English)
- summarize_de_p (the same in German)

## diigo_api.py

Functions to access and manipulate bookmarks in an account on diigo.com - see [diigo_api.md](diigo_api.md) for a description of what I know about the diigo API so far. Code contains access functions as well as use cases. 

Look at ```diigo_api.py``` for a more thorough description of each call and its parameters. 

#### The official Diigo API

Diigo offers an API that has just two function - meh. I found a third one, but that's it. You need user, password, and an additional API key for them to work. 

Not only are these functions inconvenient to use, they seem to be heavily rate-limited as well. More than a couple of dozen calls per ten minutes causes the Diigo server to refuse the requests. 

- **get_diigo_bookmarks** gets a paginated list of the most recent bookmarks
- **probe_diigo_api** checks whether user, password, and API key are valid, and bookmarks can be retrieved via get_diigo_bookmarks
- **write_diigo_bookmark** creates, or overwrites, an unique bookmark, as determined by URL and title. If these already exist, the bookmark is overwritten. 
- **delete_diigo_bookmark** deletes a bookmark identified by URL and title. 

### The interaction API

These are function calls that are used by the Diigo website, and can be used for external calls as well. They are authenticated not by the API key but by session cookies from a valid Diigo browser session. 

These function calls are all named dia_ here, short for: Diigo Interaction API. 

- **probe_dia** tests an existing requests session whether there are valid session cookies, and the DIA can be reached
- **dia_session_authenticate** uses Selenium to open a browser session where the user has to authenticate; it writes the session cookies from this session to a YAML file where the other commands can use them.
- **dia_login** tries to get valid session cookies for using with the DIA. If they can be found on disk, that's fine; if there aren't any valid session cookies, the routine calls on dia_session_authenticate to get and save session cookies. **Call dia_login** first to get the DIA running. 
- **dia_load_user_items** gets a paginated list of bookmarks (each a dictionary) 
- **dia_search_user_items** gets a paginated list of bookmarks (each a dictionary), filtered by a search term 
- **dia_get_id** returns a list of bookmark ```list_id``` values for a bookmark query
- **dia_write_** creates, or overwrites, a bookmark. 

### The Bulk API

Function calls to bulk-manipulate bookmarks, saving you a hundred single function calls with one bulk call. Unfortunately, they need some unknown extra method to authenticate, and don't work yet.

- **dia_delete_b**
- **dia_change_mode_b**

### Function calls to perform tasks

- **test_diigo_api** tests the official API as well if the DIA with a write-read-modify-delete sequence
- **dia_privatize** sets all bookmarks in the library to 'private'
- **dia_export_delete** gets all bookmarks from the Diigo account, saves them to a CSV dump file, creates them in Nextcloud if wanted, and removes them from Diigo. 
- **diigo_export_delete** tries to get/save bookmarks and delete them via the official API only. Dead slow and error-prone. 

## nc_bookmarks_api.py

- **probe_nc_bookmarks_url** looks for a Nextcloud instance at the given URL. 
- **probe_nc_bookmarks** tries to reach the Nextcloud Bookmarks app via its API.
- **create_nc_bookmark** creates a bookmark in Nextcloud
- **edit_nc_bookmark** updates a bookmark, or creates it from scratch
- **get_nc_bookmarks** retrieves a list of bookmarks matching given tags and search word
- **find_nc_bookmark** returns a NC bookmark ID for that given URL
- **get_nc_dump** returns a data frame with the most recent bookmarks

- **get_nc_folders** returns IDs of all folders in the root folder
- **get_nc_folder** returns the ID of the folder matching a regex
- **get_nc_folder_id** checks where there is actually a folder wiht that name
- **create_nc_folder** creates it. 

## process-py

#### Subroutine: describe
- If there is a human description, check if valid and add LLM page description
- If there is none, create

#### Subroutine: Tag cleaner
- Look for all tags that appear only once
- look for all bookmarks that are untagged (or with tag no_tag)

#### etc

- Check if website is still available
- If yes, do LLM summary, Create in "imported" folder
- if no, create in OBSOLETE- folder 

## Format of description

f"""
{description}
 # BOOKMARKED
{created_at}
 # LLM_DESCRIPTION
{suggested}
 # ANNOTATIONS
"""

# Todo/additional info

## Nice to have
- Check for unavailable bookmarks, and mark/tag as obsolete
- Write created_at to "added" Unix ts (which is not in the API) (possible via SQL data base access: os)

## Database access

database-5015790379; Datenbank: dbs12878957
- Table: oc_bookmarks
    - id
    - url
    - title
    - user_id
    - description
    - added
    - lastmodified
    - clickcount
    - last_preview
    - available
    - archived_file
    - html_content
    - text_content

archived_file, html_content and text_content seem to be empty. 

## Diigo CSV format
title,url,tags,description,comments,annotations,created_at

Highlights are stored with the word "Highlight: " in annotations, so just add these text
Tags are separated by a space. 