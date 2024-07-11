# nc_llm_improve.py
#
# Get a dump of all bookmarks from Nextcloud, 
# look for those without a description, and have an LLM
# suggest a description. 
#
# Also, make a dict of all tags and their frequency, 
# and filter out those that have been used only once. 
# Try suggesting similar tags. 
# 
# Script is supposed to be running in the background as it
# will definitely take indefinitely. 


from config import *
from process import * 
from nc_bookmarks_api import *

if __name__ == "__main__":
    # Import config
    # Try to reach NC bookmarks
    if not probe_nc_bookmarks():
        print("Nextcloud unreachable. Returning.")
    # Get folder ID for marking unreadable bookmarks
    nc_unread_folder = get_nc_folder(UNREAD_FOLDER)
    p = 0
    # Smaller stepwidth, loading the bookmarks is negligible
    print(f"Batch progress: (.) Reading (x) Checking (^) Website unreachable (@) AI reflecting (*) Done")
    nc_df = get_nc_bookmarks(page=p, limit = 10)
    while len(nc_df) > 0:
        # print 10 markers to show progress
        print("..........\b\b\b\b\b\b\b\b\b\b",end="", flush=True)
        # Step through bookmarks
        for b in nc_df:
            print("^",end="", flush=True)
            url = b['url']
            description = b['description']
            # Bookmark already prepared for LLM description?
            if '# LLM_DESCRIPTION' in description:
                # Check whether there is still a placeholder, otherwise, 
                if '###LLM###' in description: 
                    print("\b@",end="", flush=True)
                    llm_description = suggest_description(url,description,silent = True)
                else: # already has a LLM description   
                    llm_description = "" 
            else: # No LLM description, native bookmark not set by importer
                print("\b@",end="", flush=True)
                llm_description = suggest_description(url,description,silent = True)
                if not (llm_description == None):
                    description = description + "# LLM_DESCRIPTION\n###LLM###"
            if llm_description == None: 
                # Site is unreachable
                print("\bx",end="", flush=True)
                if nc_unread_folder not in b['folders']:
                    b['folders'].append(nc_unread_folder)
            else:
                # Upload modified description
                description = description.replace("###LLM###",llm_description)
                b['description'] = description
                edit_nc_bookmark(b)
                print("\b*",end="", flush=True)
        p += 1
        nc_df = get_nc_bookmarks(page=p, limit = 10)    
    input("Done - press ENTER to return")
