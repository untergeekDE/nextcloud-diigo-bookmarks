# process.py
#
# Routines to enhance and process the bookmarks

import requests
from bs4 import BeautifulSoup
import ollama
import json
 
from config import *

def tag_process(s):
    # Take a comma-separated string, split into substrings, and 
    # reformat these. 
    t = str(s)
    tags_list = t.split(',')
    tags_list = [t.strip().lower() for t in tags_list]
    tags_list = [t.replace("_"," ") for t in tags_list]
    return tags_list

def convert_to_dict(l):
    d = {}
    for t in l:
        if t not in d:
            d[t] = 1
        else:
            d[t] += 1
    
    # Sort the dictionary by frequency (values) in descending order
    sorted_d = dict(sorted(d.items(), key=lambda x: x[1], reverse=True))
    return sorted_d
#

def better_desc(d1,d2):
    # Pick the "better" of two descriptions - if one of them is empty, return the other, 
    # if both are non-empty, compare, if not identical, merge. 
    if len(d1) == 0: 
        return d2
    if len(d2) == 0:
        return d1
    if d1 == d2: 
        return d1
    return d2 + "# PREVIOUS\n" + d1

def suggest_description(url):
    # Fetch the webpage content
    response = requests.get(url)
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract the main text content
        title = soup.find('title').string
        main_content = soup.get_text()
                
        # Generate a summary using the Aya model
        sys_p = summarize_prompt
        summary_string = f"""
        URL: {url}
        TITEL: {title}
        INHALT: {main_content}
        """
        messages = [{
            'role': 'system',
            'content': sys_p
        },
        {
            'role': 'user',
            'content': summary_string
        }]
        options = {'temperature':0.3}
        try:
            llm_response = ollama.chat(model='aya', 
                                       messages=messages,
                                       options=options)
            return llm_response['message']['content']
        except ollama.ResponseError as e:
            print(f"Could not query LLM via ollama: {e.error}")
            return ""
    else:
        print(f"Failed to fetch the webpage. Status code: {response.status_code}")
        return None
     #

def suggest_tags(bookmark):
    # Get LLM assessment of bookmarks for this bookmark.
    # bookmark is a dict containing: 
    # - url
    # - title
    # - description (including LLM summary)
    # - tags (existing tags)
    return

def write_bookmarks_file(bookmarks_dict, lastdate):
    # Where do I get lastdate, the date of the last bookmark?
    # Haven't properly thought this through yet. 
    export_dict = {
        'lastdate': lastdate,
        'data': bookmarks_dict
    }
    with open(tags_path, 'w') as f:
        json.dump(export_dict, f)
    


def retrieve_all_tags():
    # Looks for a tag file to save time. 
    # If there is none, create it: 
    # - Get all bookmarks
    # - Write date of last bookmark stored 
    # - Write JSON of all bookmarks
    return None

def improve_bookmark(b):
    
    return False