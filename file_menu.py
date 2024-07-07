# file_menu.py
#
# Simulates a file selector box with the console-menu library:
# - Start with given path
# - List all directories, and all files matching extension pattern
# - Allow user to traverse through directories, or to select a file
# - Returns the path to a file

import os
from consolemenu import ConsoleMenu, SelectionMenu
from consolemenu.items import FunctionItem, SelectionItem

from config import *

# Auxiliary function sets file name to return
def set_f(f):
    global filename
    filename = f
    return f

def file_menu(path,extension):
    while True:
        if path[0] == '~':
            path = os.path.expanduser(path)
        path = os.path.abspath(path)
        if os.path.isdir(path):
            dir = path
        else:
            dir = os.path.dirname(path)
        # List directories in this path
        directories = [d for d in os.listdir(dir) if os.path.isdir(os.path.join(dir, d))]
        directories.sort()
        files = [f for f in os.listdir(dir) if f.endswith(extension)]
        files.sort()
        # Create list  with entries for all directories
        menu_list = ['<HOME DIR>','<PARENT> ..']
        for d in directories: 
            menu_list.append(f"<DIR> {d}")
        for f in files: 
            menu_list.append(f)
        selection = SelectionMenu.get_selection(menu_list,
                                                "Select a file or directory",
                                                f"{dir}")
        # Home Directory selected?
        if selection == 0:
            path = "~/dummy.txt"
        elif selection == 1: 
            path = os.path.join(dir,"../dummy.txt")
        elif selection == len(menu_list):
            # Exit option - No file selected
            return None
        elif selection > len(directories)+1:
            # File selected
            s = selection - len(directories) - 2
            return os.path.join(dir,files[s])
        else:
            # Continue while loop but with different directory
            path = os.path.join(dir, directories[selection-2]+"/.")


# Short demo of the file selector box as a TXT viewer: 
if __name__ == "__main__":
    f = file_menu(".",".txt")
    if f:
        print(f"Dumping file 'f':")
        with open(f, 'r') as file:
            for i, line in enumerate(file):
                print(line.strip())
                if i % 10 == 0:
                    input("")
        print('----EOF----')
    else:
        print("No file selected.")

