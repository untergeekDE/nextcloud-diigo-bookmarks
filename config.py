# config.py
# 
# Settings and absolute paths

VERSION_STRING = "nextcloud-diigo-bookmarks V0.5.2"

# Enables requests session logging to the terminal
# LOG = 1
LOG = 0

DIIGO_URL = "https://secure.diigo.com/api/v2/"

CONFIG_PATH = "~/.ncdbookmarks/config.yaml"
SAMPLE_CONFIG_PATH = "./sample_config.yaml"
SESSION_PATH = "~/.ncdbookmarks/session_cookies.yaml"

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
DIIGO_FIELDS_LIST = ['title',
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
NC_FIELDS_LIST = ['title',
                  'url',
                  'description',
                  'tags',
                  'folders']
# Note that you don't get a creation or modification date. This is generated automatically
# in the app, and cannot be modified by the API. Unfortunately. 

nc_credentials = False
diigo_credentials = False

AUTH_HEADERS = {
    "Accept": "application/json",
    "Authorization": "basic",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"     
}

############ Functions to get and set global config variable ############
"""
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
    "diigo_dump_path": "",
    "nc_dump_path": "",
    "diigo_batch_size": 100,
    "nc_batch_size": 100,
    "ollama": {
        "model": "",
    }
}
"""
import os
import yaml

def get_yaml(path):
    # Expand home directory
    path = os.path.expanduser(path)
    # Check whether there's a file with the passwords
    if os.path.exists(path):
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return data
    else: 
        return None

def get_config(path):
    if 'config' in globals():
        if config is not None:
            return config
    return get_yaml(path)

def write_config(path,config):
    path = os.path.expanduser(path)
    # Check whether directory exists and create if necessary
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.mkdir(directory)
    with open(path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False) 
    
def setup_config_dir():
    """
    If the key.YAML file in the .ncdbookmarks dir does not exist, 
    - create directory
    - copy sample YAML file there
    Return True if this was done, False if key.yaml already exists.
    """
    import stat
    # Expand the path if it contains '~'
    path = os.path.expanduser(CONFIG_PATH)
    if os.path.exists(path):
        return False
    # Check whether directory exists and create if necessary
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.mkdir(directory)
    # Set permissions to rw------- (700 in octal)
    os.chmod(directory, stat.S_IRUSR | stat.S_IWUSR | stat.S_IEXEC)
    sample_config = get_config(SAMPLE_CONFIG_PATH)
    write_config(path,sample_config)
    return True

# config
# Global variable nastiness
config = get_config(CONFIG_PATH)

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
