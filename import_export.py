# upload_bookmarks.py
#
# 

import os
import pandas as pd

from config import *
from process import *
from file_menu import file_menu, proceed
from nc_bookmarks_api import probe_nc_bookmarks, get_nc_bookmarks, get_nc_diigo_folder, find_nc_bookmark, create_nc_bookmark

# import the CSV with the Diigo bookmarks
"""
bookmarks_df format:
- index         (int)   unique id
- title         (str)   webpage title
- url           (str)   URL
- tags          (list)  comma-separated list of str, "no tag" if empty
- description   (str)   descriptory text
- comments      (str?)  empty
- annotations   (str)   string, quoting highlighted text beginning with "Highlight: "
- created_at    (datetime)         
"""

# Read bookmarks CSV file and return
def get_bookmarks(b_path):
    path = os.path.expanduser(b_path)
    if os.path.exists(path):
        b_df = pd.read_csv(path, index_col=False)
        return b_df
    else:
        raise FileNotFoundError(f"Key file {path} not found")

# Read bookmarks CSV but keep only valid bookmarks
def read_diigo_bookmarks(b_path):
    df = get_bookmarks(b_path)
    df = df[DIIGO_FIELDS_LIST]


# Add bookmarks to a bookmarks CSV file. Rudimentary error checking.
# 
def update_bookmarks(b_path, b_df):
    b_path = os.path.expanduser(b_path)
    # Check whether directory exists and create if necessary
    directory = os.path.dirname(b_path)
    if not os.path.exists(directory):
        os.mkdir(directory)
    
    # Use Diigo-style CSV data for compatibility.
    # check b_df
    # Special: Rename column 'desc' to  'description'
    if 'desc' in b_df.columns:
        b_df = b_df.rename(columns={'desc': 'description'})

    # Check: Are those columns in the source file?
    # (Additional columns are kept.)
    # Does it contain 'folders' column? If yes, it's a Nextcloud file.
    if 'folders' in b_df.columns.to_list():
        missing_columns = [i for i in NC_FIELDS_LIST if i not in b_df.columns.to_list()]
    else: 
        missing_columns = [i for i in DIIGO_FIELDS_LIST if i not in b_df.columns.to_list()]    
    if missing_columns != []:
        print(f"ERROR: Missing columns {missing_columns}")
        print(f"Bookmarks dataframe contains these columns: {list(b_df.columns)}")
        return None
    # Read 
    try:
        old_df = get_bookmarks(b_path)
    except:
        # File not found, create empty df
        # Create a new dataframe with the columns from `b_columns`
        old_df = pd.DataFrame(columns=b_df.columns)
    # Join b_df and drop duplicate entries
    new_df = pd.concat([old_df, b_df], ignore_index=True)
    new_df = new_df.drop_duplicates(subset=['url','title'])
    new_df.to_csv(b_path, index=False)
    return new_df

def write_to_log(log_path,text):
    if not os.path.exists(log_path):
        text = "STARTING...\n" + text
    with open(log_path, 'a') as f:
        f.write(text + '\n')
    return True

def move_backup(b_path):
    if os.path.exists(b_path):
        i = 0
        backup_path = f"{b_path}.{i}.bak"
        # Find a name for the backup copy
        while os.path.exists(backup_path):
            i += 1
            backup_path = f"{b_path}.{i}.bak"
        os.rename(b_path,backup_path)

def inspect_file(path): 
    try:
        df = get_bookmarks(path)
    except:
        print(f"ERROR: Could not read file '{path}'")
        return None
    print(f"File '{path}' contains {len(df)} bookmarks. First lines:")
    print()
    print(df.head(5))
    # Look at the columns - put them into a list
    columns = df.columns.to_list()
    print()
    print(f"Contains these columns (*starred* columns are necessary):")
    for c in columns: 
        print(f"*{c}*" if c in NC_FIELDS_LIST else str(c),end=", ")
    input("\nPress ENTER to continue")


# Get a CSV, convert and upload to Nextcloud. 
def upload_nc_bookmarks(b_path):
    nc_key = config['nc_bookmarks']['password']
    probe_nc_bookmarks()
    bookmarks_df = get_nc_bookmarks(b_path)
    print(bookmarks_df.head(5))
    diigo_folder = get_nc_diigo_folder()
    diigo_df = get_bookmarks(b_path)
    # tags ist ein String, müssen wir erst splitten - 
    # und wenn wir dabei sind, gleich klein schreiben.
    print(f"Number of bookmarks: {len(diigo_df)}")
    l = []
    for t in diigo_df['tags']:
        l.extend(tag_process(t))
    d = convert_to_dict(l)
    # Write bookmarks to Diigo folder
    for i in range(0,len(diigo_df)):

        title = str(diigo_df['title'][i])
        url = str(diigo_df['url'][i])
        tags = tag_process(diigo_df['tags'][i]) # Split and clean
        description = str(diigo_df['description'][i])
        if description == "nan":
            description = ""
        annotations = str(diigo_df['annotations'][i])
        if annotations== "nan":
            annotations=""
        created_at = str(diigo_df['created_at'][i])

        # Create description containing all information 
        llm = '###LLM###'
        desc = f"""{description}

# BOOKMARKED
{created_at}

# LLM_DESCRIPTION
{llm}

# ANNOTATIONS
{annotations}
"""
        # Get dict of bookmark if exists
        print(f"Bookmark {i+1} of {len(diigo_df)}:")
        print(url)
        d = find_nc_bookmark(url=url,folder_id=diigo_folder)
        if len(d) == 0:
            # If descriptions already contains # BOOKMARKED etc., keep it
            if ('# BOOKMARKED' in description) and ('# ANNOTATIONS' in description):
                desc=description
            # Creating bookmark
            print(title)
            print(desc)
            r = create_nc_bookmark(url=url,
                title=title,
                description=desc,
                tags=tags,
                folders=[diigo_folder])
            print(f"Created with id {r}")
        else:
            for dd in d:    
                if title==dd['title']:
                    print(f"Bookmark exists for URL {url}")
                else:
                    print(f"Different bookmark for same URL. Modify.")
                    id = dd['id']
                    data = {
                        # Take the title of the bookmark with the longer description
                        'title' : title if len(description) > len(dd['description']) else dd['title'],
                        'description': better_desc(desc,dd['description']),
                        # Merge, removing duplicate tags
                        'tags': list(set(tags + dd['tags'])),
                        'folders': [folder_id]
                    }
                    r = edit_nc_bookmark(data,id)
                    print(f"Modified id {r}")

def get_nc_dump(dump_path = None):
    df = pd.DataFrame()
    p = 0
    nc_batch_size = config['nc_batch_size']
    print(f"Downloading Nextcloud bookmarks in batches of {nc_batch_size}")
    data = get_nc_bookmarks(page = 0, limit = nc_batch_size)
    while len(data) > 0: 
        print(".",end="", flush=True)
        b_df = pd.DataFrame(data)
        df =  pd.concat([df, b_df], ignore_index=True)  
        if dump_path != None:
             update_bookmarks(dump_path,b_df)
        p += 1
        print("\b*",end="", flush=True)
        data = get_nc_bookmarks(page = p, limit = nc_batch_size)
    return df
              
# Select and upload CSV to Nextcloud
def import_nc_csv(f):
    s = 1
    while s == 1: 
        f = file_menu("Select CSV file to import into Nextcloud",config['nc_dump_path'],".csv")
        inspect_file(f)
        s = proceed(f"Upload bookmarks file {f} to Nextcloud installation at {config['nc_bookmarks']}")
        # If s == 1, try again
    if s == 2: # Abort
        return
    upload_nc_bookmarks(f)

def import_diigo_csv(f):
    s = 1
    while s == 1: 
        f = file_menu("Select CSV file to import into Nextcloud",config['diigo_dump_path'],".csv")
        inspect_file(f)
        s = proceed(f"Upload bookmarks file {f} to Diigo account {config['diigo']['user']}")
        # If s == 1, try again
    if s == 2: # Abort
        return
    upload_diigo_bookmarks(f)


# Exports all Nextcloud bookmarks to a CSV file in the selected directory. 
# User may change directory and file name
def export_nc_csv(f):
    global config
    config = get_config(CONFIG_PATH)
    s = 1 # Selection
    while s == 1:
        f = file_menu("Select CSV to write to. \n\n\
                    To create a new file, just browse to the target directory and leave the menu. ",
                    f,".csv")
        if os.path.isdir(f):
            fname = input(f"Saving to directory {f}\nEnter file name: ")
            if fname[-4:] != '.csv':
                fname += ".csv"
            f = os.path.join(f,fname)
        s = proceed(f"Ready to dump Nextcloud bookmarks to {f}")
        # If s == 1, try again
    if s == 2: # Abort
        return
    probe_nc_bookmarks()
    print("Retrieving bookmarks from Nextcloud")
    df = get_nc_dump(f)
    print("")

if __name__ == "__main__":
    global config
    config = get_config(CONFIG_PATH)
    import_nc_csv(config['nc_dump_path'])