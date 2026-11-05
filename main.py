#!/usr/bin/env python3

import os 
import json
import subprocess
import sys 

is_windows_os = sys.platform.startswith('win')

path_separator = os.sep
import re

current_dir = os.path.dirname(__file__)

CONFIG_PATH = os.path.join(current_dir, 'config.json')
CONFIG = {}

ROOT_DIR = None

FILES = ()
FILES_CACHE = {}
PATH_MATCHES = []
TEXT_MATCHES = []

PATH_REGEX = re.compile(r'^[^/]+(/.+)?/?$')
TEXT_REGEX = re.compile(r'[,:\.]')

def main():
    global CONFIG, ROOT_DIR
    print("\n" + "#" * 32)
    print(('-' * 10) + 'NOTES HELPER' + ('-' * 10))
    print("#" * 32 + "\n")



    CONFIG = load_config()
    ROOT_DIR = CONFIG.get('path')
    populate_files()

    while True:
        try:
            print('\n\n' + '=' * len('**** MAIN MENU ****'))
            print('     MAIN MENU     ')
            print('=' * len('**** MAIN MENU ****') + '\n')
            print('0    Search')
            print('1    Create')

            while True:
                choice = input('\n Choose an option : ')   
                try:
                    validated = int(choice.strip())
                    if validated in (0,1):
                        break
                    print('\nError, choose an existing submenu')
                    continue
                except Exception:
                    print('\nPlease choose a valid index number')
                    continue

            if validated == 1:
               create_note()

            if validated == 0:       
               search_inputs()

        

        except KeyboardInterrupt:

            while True:
                choice = input('\n\nDo you really want to quit ? (yes, no , reload) : ')

                if choice.lower().strip() in ('y', 'yes'):
                    os._exit(0)

                elif choice.lower().strip() in ('n', 'no'):
                    break

                elif choice in ('r', 'reload'):
                    print('\nReloaded ...')
                    print('\n' + ('-' * 32) + '\n')
                    populate_files()
                    break

                else:
            
                    continue
               



def load_config():
    if not os.path.exists(CONFIG_PATH):
       config =  run_setup()
        
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
        if not config or not config.get('path'):
            config = run_setup()

        else:
            print(f"Use existing config ? {config.get('path')}")
            while True:
                
                confirm = input('yes or no ? ')
                if confirm.lower().strip() in ('y', 'yes'):
                    break

                elif confirm.lower().strip() in ('n', 'no'):
                    config= run_setup()
                    
                else: 
                    print('\nEnter: "yes" or "no" .')
                    continue

    return config
    

def run_setup():


    print('\nEntering setup')
    print('-' * 32)


       
    note_folder = input("\nNotes folder path : ")
   
       
    with open(CONFIG_PATH, 'w') as f:
        f.write(json.dumps({'path': note_folder}))
    print(('-' * 32) + '\n')
    return {'path': note_folder}
   

def populate_files():
    global FILES, PATH_MATCHES, TEXT_MATCHES, FILES_CACHE
    FILES_CACHE = {}
    PATH_MATCHES = []
    TEXT_MATCHES = []
    
    FILES = tuple(
        os.path.join(root, f)
        for root, _, files in os.walk(ROOT_DIR)
        for f in files
        if f.endswith('.md') or f.endswith('.txt')
    )    

    for f in FILES:
        with open(f, 'r') as c:
            
            content = c.read().strip().lower()
            words  = set(TEXT_REGEX.sub("", content).split())
 
            sub_path = f.replace(ROOT_DIR, '')
            subbed_path = sub_path

            root = sub_path.split(path_separator)[0]

            split_path = subbed_path.lower().split(path_separator)

            file_name = split_path[-1].split('.')[0]
            
            filename_tokens = get_filename_tokens(file_name)

            FILES_CACHE[f] = {'root': root, 'tokens': filename_tokens, 'split_path': split_path, 'words': words}

  
def create_note():
    global CONFIG

    while True:
        full_dir = None
        validated_choice = None
        print('\n\n' + '=' * len('    NOTE CREATION    '))
        print('    NOTE CREATION    ')
        print('=' * len('    NOTE CREATION    '))
        print('Press q to go back ')
        location = input("\nSearch a directory (e.g. python), press enter for guidance : ")

        if location.strip().lower() == 'q':
            return
        
        known_folders = set()
        root_folders = []
    
        
        for idx, (dir_path, dirs,_) in enumerate(os.walk(ROOT_DIR)):
            if idx == 0:
                root_folders = dirs
            for d in dirs:

                full_path = os.path.join(dir_path, d)
                known_folders.add(full_path.replace(ROOT_DIR, '').strip())



        if location == '':
            print('\n')
            for idx, m in enumerate(root_folders):
                print(str(m))  

            continue
            

        
        else:
            token_per_paths = {d: d.split(path_separator) for d in known_folders}

            match = [key for key, val in token_per_paths.items() if location.lower().strip() in set(v.lower() for v in val)]
        
   

        if match:
    
            match.sort()     

            print('\n')
            for idx, m in enumerate(match):
                print(str(idx) + ((12 - len(str(idx))) * " ") + str(m))

            while True:
                choice = input('\nSelect a directory (0-999) : ')

                if choice.strip().lower() == 'q':
                    break
                try:
                    validated_choice = int(choice.strip())
                    break

                except Exception:
                    print('\nPlease choose a valid index number')
                    continue
        else:
            while True:
          
                path = input('\nNo match, enter a new path (e.g. "Python/Basics") : ')

                if path.lower().strip() == 'q':
                    break


                if not PATH_REGEX.match(path):
                    print('A relative path should follow this format : Python/Basics\n')
                    continue
               
                full_dir = os.path.join(ROOT_DIR, path)
                
                os.makedirs(full_dir, exist_ok=True)
                print(f'Created : {full_dir}')
                break


        if full_dir or validated_choice is not None:
      
            filename = input('\nName this note (e.g. new_note python) : ')

            if filename == 'q':
                continue
             
            full_path = os.path.join(full_dir, filename) if full_dir else os.path.join(ROOT_DIR, match[validated_choice], filename)

            if not os.path.exists(full_path):
                open(full_path, 'w')
               

            open_file(full_path)

            return


def search_inputs():
    global PATH_MATCHES, TEXT_MATCHES



    while True:
        PATH_MATCHES = []
        TEXT_MATCHES = []
        parsed = None
        print('\n\n' + '=' * len('    NOTE SEARCH    '))
        print('    NOTE SEARCH    ')
        print('=' * len('    NOTE SEARCH    '))

        while True:
            
            string = input('\nSearch (e.g. python core) or q : ').strip().lower()

            if string == 'q':
                return

            split_str = string.split(" ")

            try:
                for path, data in FILES_CACHE.items():
                   

                        filename_tokens = data.get('tokens', None)

                        if not filename_tokens:
                            continue

                        words = data.get('words')
                        root = data.get('root')
                        split_path = data.get('split_path')


                        if len(split_str) > 1:
                            if split_str[0] in split_path:

                                if split_str[1] in (*filename_tokens, *split_path):
                                    update_results(path, 'path_match', root)

                                elif split_str[1] in words:
                                    update_results(path, 'text_match', root)
            
                        
                        elif (string in split_path) or (string in filename_tokens):

                            update_results(path, 'path_match', root)

                        elif (string in words or string in filename_tokens):
                            
                            update_results(path, 'text_match', root)

                break
            
            except FileNotFoundError:
                print('\nSome files have changed , reloading ...')
                populate_files()
                continue

   

        if not PATH_MATCHES and not TEXT_MATCHES: 
            print('No result matching query ...')
            continue
        


        if TEXT_MATCHES:
            TEXT_MATCHES.sort(key=lambda x: x.get('filename'))
            print(f'\n' + ('#' * 10) + ' TEXT MATCH ' + ('#' * 10) + '\n')

            for idx, r in enumerate(TEXT_MATCHES):
                print(process_file(r, idx))


        if PATH_MATCHES:
            print(f'\n' + ('#' * 10) + ' PATH MATCH ' + ('#' * 10) + '\n')
            PATH_MATCHES.sort(key=lambda x: x.get('filename'))

            for idx, f in enumerate(PATH_MATCHES, start=len(TEXT_MATCHES)):
                print(process_file(f, idx))
            
        while True:

            index = input('\n\nEnter a number or press "q" to go back : ')
            print('-' * len('Enter a number or press "q" to go back :  '))

            if index.strip().lower() == 'q':
                break

            try:
                parsed = int(index.strip())


                if parsed > len(TEXT_MATCHES):

                    open_file(PATH_MATCHES[(parsed - len(TEXT_MATCHES)) - 1].get('path'))

                elif parsed > 0:
                    open_file(TEXT_MATCHES[parsed - 1].get('path'))

                else:
                    continue

                break

            except:
                print('Invalid number, try again ...')
                continue
    
def process_file(r:dict, idx):
    file_name = r.get('filename')
    root = r.get('root')
    parent_dir = r.get('path').split(path_separator)[-2]
    helper_str = rf"→ {root}\..\{parent_dir}" if root.lower() != parent_dir.lower() else f"→ {root}"
    f_len = len(file_name)
    return f"{idx + 1})" + " " * (4 - len(str(idx + 1))) + f"{file_name}" + " " * (30 - f_len) + helper_str

def update_results(path:str, type:str, root:str):
    global PATH_MATCHES, TEXT_MATCHES
    if type == 'path_match':
        PATH_MATCHES.append({'filename': path.split(path_separator)[-1], 'path': path, 'type': 'path_match',
                                                                         'root': root})
    else:
        TEXT_MATCHES.append({'filename': path.split(path_separator)[-1], 'path': path, 'type': 'text_match',
                                                                         'root': root})


def open_file(path):
    program = "mousepad" if not is_windows_os else 'notepad.exe'

    subprocess.Popen([program, path]) 

def get_filename_tokens(fname:str):

    if '.' in fname:
        print(f'Dots detected in {fname}, only underscores or spaces are allowed ...')
        return None
    
    if '-' in fname:
        if not 'safebackup' in fname:
             print(f'Dash detected in {fname}, only underscores or spaces are allowed ...')
        return None        
    
    elif '_' in fname and not " " in fname:
        return fname.split('_')
    
    elif ' ' in fname and not '_' in fname:
        return fname.split(' ')

    elif '_' in fname and ' ' in fname: 

        return [token for chunk in fname.split(' ') for token in chunk.split('_')]
      
    else:
        return [fname]

main()

