# import_csv.py

import os
import pandas as pd

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
def get_bookmarks(b_path):
    path = os.path.expanduser(b_path)
    if os.path.exists(path):
        b_df = pd.read_csv(path, index_col=False)
        return b_df
    else:
        raise FileNotFoundError(f"Key file {path} not found")


# Add bookmarks to a bookmarks CSV file. Rudimentary error checking.+
# 
def update_bookmarks(b_path, b_df):
    # Use Diigo-style CSV data for compatibility.
    b_columns = ['title',
                 'url',
                 'tags',
                 'description',
                 'comments',
                 'annotations',
                 'created_at']
    # check b_df
    # Special: Rename column 'desc' to  'description'
    if 'desc' in b_df.columns:
        b_df = b_df.rename(columns={'desc': 'description'})
    if list(b_df.columns) != b_columns:
        print(f"ERROR: Bookmarks dataframe contains these columns: {list(b_df.columns)}")
        return None
    # Read 
    try:
        old_df = get_bookmarks(b_path)
    except:
        # File not found, create empty df
        # Create a new dataframe with the columns from `b_columns`
        old_df = pd.DataFrame(columns=b_columns)
    if list(old_df.columns) != b_columns:
        print(f"WARNING: Bookmarks CSV contains these columns: {list(b_df.columns)}")
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