# main.py
#
# Extremely simple command-line tool to get and manipulate bookmarks
# via the Diigo and Nextcloud Bookmarks API, respecively

import getpass
from datetime import datetime

from consolemenu import ConsoleMenu
from consolemenu.items import FunctionItem, SubmenuItem, CommandItem

from file_menu import file_menu

from config import *

from process import tag_process, convert_to_dict
from nc_bookmarks_api import probe_nc_bookmarks, probe_nc_bookmarks_url
from diigo_api import dia_login, probe_dia, dia_export_delete, dia_privatize
from diigo_api import probe_diigo_api, probe_dia
from import_export import import_nc_csv, export_nc_csv, inspect_file

############### Menus #####################

def get_nextcloud_url():
    global config
    nc_url = config['nc_bookmarks']['url']
    # Probe via requests
    while not probe_nc_bookmarks_url(nc_url):
        nc_url = input("Enter URL of your Nextcloud installation: ")
    config['nc_bookmarks']['nc_url'] = nc_url
    write_config(CONFIG_PATH,config)
    return True

def get_nextcloud_credentials(): 
    global config
    while not probe_nc_bookmarks():
        config['nc_bookmarks']['user'] = input("Enter your Nextcloud username: ")
        config['nc_bookmarks']['password'] = getpass.getpass("Enter your Nextcloud password: ")
        write_config(CONFIG_PATH,config)
    return True

def inspect_dump_csv_files(path):
    # Get a list of csv files and allow user to select one of them to view
    # TODO: List csv.0.bak ... csv.x.bak as well
    filename = file_menu("Select file to inspect",path,".csv")
    if not os.path.isdir(filename):
        inspect_file(filename)
        return filename
    else:
        None

############### Actual processes ###############
def process_nc_bookmark_tags():
    """
    - Read all nc bookmarks via API
    - Create a dict of all tags
    - Assign all bookmarks that have no tags, or use unique tags, to a folder
    - Try improving the bookmarks:
        - Create a dict of tags with the shortest Levenshtein distance for each tag
        - Use it to remove obvious spelling errors
        - 
    """
    return None

def dummy(remove_diigo=True,
                      use_llm = True,
                      create_nextcloud = True):
    print("Not implemented yet. Sorry. ^_^")
    input("Press Enter to continue")


if __name__ == "__main__":
    print(VERSION_STRING)
    # Do we have valid credentials?
    # Look for config dir at path key_path (~/.ncdbookmarks), if it doesn't exist: 
    # Setup config dir with the right permissions
    setup_config_dir()
    global config
    config = get_config(CONFIG_PATH)
    # Nextcloud bookmarks API reachable?
    if get_nextcloud_url():
        print("Yes, I can reach your Nextcloud. Checking credentials...")
    if probe_nc_bookmarks():
        print("Yes, your user credentials for Nextcloud are valid.")
    # Do the same thing with the Diigo Interaction API. 
    session = dia_login()
    diigo_credentials = probe_dia(session)
    session.close()
    print("Yes, I found a valid Diigo session to use with the API.")
    ### Define the menus ###
    main_menu = ConsoleMenu("Main Menu", "So what do you wish to do now?")
    ### Submenu: Diigo
    diigo_menu = ConsoleMenu("Diigo Menu", "Get and remove your Diigo bookmarks")
    diigo_menu.append_item(FunctionItem("Set all Diigo bookmarks to private", 
                                  dia_privatize))
    diigo_menu.append_item(FunctionItem("Export Diigo bookmarks to file", 
                                  dia_export_delete,
                                  kwargs={"remove_diigo":False,
                                          "use_llm":False,
                                          "create_nextcloud":False}))
    diigo_menu.append_item(FunctionItem("Export and remove bookmarks from Diigo",
                                  dia_export_delete,
                                  kwargs={"remove_diigo":True,
                                          "use_llm":False,
                                          "create_nextcloud":False}))
    diigo_menu.append_item(FunctionItem("Recreate Diigo bookmarks in Nextcloud", 
                                  dia_export_delete,
                                  kwargs={"remove_diigo":False,
                                          "use_llm":False,
                                          "create_nextcloud":True}))
    diigo_menu.append_item(FunctionItem("Recreate Diigo bookmarks in Nextcloud using AI to improve descriptions",
                                  dia_export_delete,
                                  kwargs={"remove_diigo":False,
                                          "use_llm":True,
                                          "create_nextcloud":True}))
    diigo_menu.append_item(FunctionItem("Full Service: Export, remove, and create in Nextcloud, improving with AI",
                                  dia_export_delete,
                                  kwargs={"remove_diigo":True,
                                          "use_llm":True,
                                          "create_nextcloud":True}))
    diigo_menu.append_item(FunctionItem("Inspect dump file(s)", inspect_dump_csv_files, [config['diigo_dump_path']]))
    ### Sub-Menu: Nextcloud
    nc_menu_text="""Export, import, and improve the Nextcloud bookmarks

    The AI-supported functions take ages, so they are detached, i.e.: 
    The task is started as a separate process running in the background. 
"""
    nc_bookmarks_menu = ConsoleMenu("Nextcloud Menu", 
                                    nc_menu_text)
    nc_bookmarks_menu.append_item(FunctionItem("Export Nextcloud Bookmarks to a CSV file", 
                                  export_nc_csv,[config['nc_dump_path']]))
    nc_bookmarks_menu.append_item(FunctionItem("Import Bookmarks CSV file to Nextcloud", 
                                  import_nc_csv,
                                  [config['nc_dump_path']]))
    nc_bookmarks_menu.append_item(CommandItem("AI-supported improvement of bookmark descriptions (DETACHED)", 
                                  "python nc_llm_improve.py"))
    nc_bookmarks_menu.append_item(CommandItem("AI-supported improvement of tags (DETACHED)", 
                                  "python process.py"))
    ### Sub-Menu: Tools
    tools_menu = ConsoleMenu("Tools Menu",
                             "Inspect and compare.")
    tools_menu.append_item(FunctionItem("Inspect CSV file", 
                                        inspect_dump_csv_files, 
                                        [config['diigo_dump_path']]))
    tools_menu.append_item(FunctionItem("Analyze bookmarks and tags in CSV file",dummy,[]))
    tools_menu.append_item(FunctionItem("Compare bookmarks",dummy,[]))
    
    ### Main Menu
    main_menu.append_item(SubmenuItem("Do things on Diigo", diigo_menu,menu=main_menu))
    main_menu.append_item(SubmenuItem("Do things on Nextcloud", nc_bookmarks_menu, menu=main_menu))
    main_menu.append_item(FunctionItem("Reauthenticate Diigo account",
                              dummy))
    main_menu.append_item(FunctionItem("Log on to another Nextcloud",
                              dummy))
    main_menu.append_item(SubmenuItem("Tools for analysis and comparison",tools_menu,menu=main_menu))
    # Run the menu
    main_menu.show()