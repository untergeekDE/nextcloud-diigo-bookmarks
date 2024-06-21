# myconfig.py
# 
# Settings and absolute paths


nc_url = "https://www.eggers-elektronik.de/nextcloud/"
nc_path = "~/key/nc.key"
nc_user = "Jan"
b_path = "data/802697_csv_2024_05_08_9389e.csv"
tags_path = "data/tags.json"

# diigo definitions
diigo_url = "https://secure.diigo.com/api/v2/"
diigo_key_path = "~/key/diigo_api.key"
diigo_pw_path = "~/key/diigo_pw.key"
diigo_user = "untergeekde"

diigo_fields_list = ['title',
                 'url',
                 'tags',
                 'desc', # Guess what: the CSV from the exporter has 'description' rather than 'desc'. Meh.
                 'comments',
                 'annotations',
                 'created_at']

global nc_key
global diigo_key
global diigo_pw

auth_headers = {
    "Accept": "application/json",
    "Authorization": "basic"
}


summarize_de_p = """
        Du bist Bibliothekar und erstellst eine Zusammenfassung 
        des Inhalts einer Website in einem Absatz. 
        """

summarize_en_p ="""
You are a librarian. Your task is to suggest a summary for the
content of a website, condensed to one paragraph.
"""

summarize_prompt = summarize_de_p
