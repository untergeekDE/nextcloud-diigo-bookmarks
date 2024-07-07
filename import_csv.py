# import_csv.py

import os
import pandas as pd

from config import *

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
def get_nc_bookmarks(b_path):
    df = get_bookmarks(b_path)
    df = df[diigo_fields_list]


# Add bookmarks to a bookmarks CSV file. Rudimentary error checking.+
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
    missing_columns = [i for i in diigo_fields_list if i not in b_df.columns.to_list()]
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