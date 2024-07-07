# myconfig.py
# 
# Settings and absolute paths

VERSION_STRING = "nextcloud-diigo-bookmarks V0.4.1 alpha"

# Enables requests session logging to the terminal
# LOG = 1
LOG = 0

diigo_url = "https://secure.diigo.com/api/v2/"

config_path = "~/.ncdbookmarks/config.yaml"
sample_config_path = "./sample_config.yaml"
session_path = "~/.ncdbookmarks/session_cookies.yaml"

b_path = "../data/802697_csv_2024_05_08_9389e.csv"
tags_path = "../data/tags.json"

# Diigo batch size for exporting and deleting -> moved to config.yaml
# diigo_batch_size = 100 
# nc_batch_size = 100

# Folder names
DIIGO_FOLDER = "DIIGO"
UNREAD_FOLDER = "LESEN"
PRIVATE_FOLDER = "PRIVAT"
UNREACHABLE_FOLDER = "Abgelaufen"
UNIQUE_TAG_FOLDER = "EinzelfallTags"

# Most relevant DIIGO fields, 
# at least, these are the fields you get in the CSV from Diigo's exporter tool.
# There is additional info on the platform like: who bookmarked something first, and
# how popular are these URLs, but they are not relevant for the import.
diigo_fields_list = ['title',
                 'url',
                 'description', 
                 # Guess what: the CSV from the exporter has 'description' 
                 # rather than 'desc'. Meh.
                 # For consistency, I expand 'desc' columns into 'description'
                 # wherever I meet them. 
                 'tags',
                 'comments',
                 'annotations',
                 'created_at']

# The NC Bookmarks fields definition is more condensed: 
nc_fields_list = ['title',
                  'url',
                  'description',
                  'tags',
                  'folder']
# Note that you don't get a creation or modification date. This is generated automatically
# in the app, and cannot be modified by the API. Unfortunately. 

nc_credentials = False
diigo_credentials = False

auth_headers = {
    "Accept": "application/json",
    "Authorization": "basic",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"     
}

# Global config
config = {
    "diigo": {
        "user": "",
        "password": "",
        "apikey": ""
    },
    "nc_bookmarks": {
        "user": "",
        "password": "",
        # URL of the NC instance
        "nc_url": ""
    },
    "auth_timestamp": "",
    "dump_path": "../data/diigo_dump.csv",
    "diigo_batch_size": 100,
    "nc_batch_size": 100,
    "ollama": {
        "model": "gemma2",
    }
}

################ LLM Prompts ###############
summarize_de_p = """
        Du bist Bibliothekar und erstellst eine Zusammenfassung 
        des Inhalts einer Website in einem Absatz. 

        Überprüfe die Beschreibung unter DESCRIPTION und ergänze. 
        """

summarize_en_p ="""
You are a librarian. Your task is to suggest a summary for the
content of a website, condensed to one paragraph.

Check the DESCRIPTION and add what is missing
"""

summarize_prompt = summarize_de_p
