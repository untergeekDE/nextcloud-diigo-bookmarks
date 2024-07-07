# upload_bookmarks.py
#
# 


from config import *
from nc_bookmarks_api import * 
from import_csv import get_bookmarks, get_nc_bookmarks
from process import *
from config_lib import get_nc_key

# import run

if __name__ == "__main__":
    nc_key = get_nc_key()
    probe_nc_bookmarks()
    bookmarks_df = get_bookmarks(b_path)
    print(bookmarks_df.head(5))
    diigo_folder = get_nc_diigo_folder()
    diigo_df = get_nc_bookmarks(b_path)
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
        d = find_nc_bookmark(url=url,folder_id=folder_id)
        if len(d) == 0:
            # Creating bookmark
            print(title)
            print(desc)
            r = create_nc_bookmark(url=url,
                title=title,
                description=desc,
                tags=tags,
                folders=[folder_id])
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
                                                


        