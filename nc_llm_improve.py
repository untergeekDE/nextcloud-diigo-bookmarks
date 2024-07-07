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

from nc_bookmarks_api import edit_nc_bookmark, 

from config import *
