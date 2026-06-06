import os 
import json
import subprocess
import sys 

is_windows_os = sys.platform.startswith('win')

path_separator = '/' if not is_windows_os else '\\'
import re

current_dir = os.path.dirname(__file__)

CONFIG_PATH = os.path.join(current_dir, 'config.json')
CONFIG = {}
FILES = set()
RESULTS = []

def main():
    global CONFIG
    print("\n" + "#" * 32)
    print(('-' * 10) + 'NOTES HELPER' + ('-' * 10))
    print("#" * 32 + "\n")



    CONFIG = load_config()
    populate_files()

    while True:
        try:
           search_inputs()

        except KeyboardInterrupt:

            while True:
                choice = input('\n\nDo you really want to quit ? (yes, no , reload) : ')

                if choice.lower().strip() in ['y', 'yes']:
                    os._exit(0)

                elif choice.lower().strip() in ['n', 'no']:
                    break

                elif choice in ['r', 'reload']:
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
                if confirm.lower().strip() in ['y', 'yes']:
                    break

                elif confirm.lower().strip() in ['n', 'no']:
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
    global FILES

    for root, _, files in os.walk(CONFIG.get('path')):
        for f in files:
            file_name = f
            if file_name.endswith('.md') or file_name.endswith('.txt'):
                FILES.add(os.path.join(root, file_name))


def search_inputs():
    global FILES, RESULTS
    RESULTS.clear()
    string = input('\nSearch : ').strip().lower()

    for path in FILES:
        with open(path, 'r') as f:
            content = f.read().strip().lower()
            words = content.split()

            subbed_path = re.sub(rf'(^{re.escape(CONFIG.get("path"))})(.+)', r'\2', path).lower()
            split_path = subbed_path.split(path_separator)
            
            if (string in split_path) or (string in subbed_path.split('.')[-2]):

                RESULTS.append({'filename': path.split(path_separator)[-1], 'path': path, 'type': 'path_match'})

            elif (string in words or string in path.split(path_separator)[-1]):
                
                RESULTS.append({'filename': path.split(path_separator)[-1], 'path': path, 'type': 'text_match'})

   

    if not RESULTS: 
        print('No result matching query ...')
        return
    
    RESULTS.sort(key=lambda x: x.get('type'), reverse=True)
    sepatation_happened = False

    if any([r.get('type')== 'text_match' for r in RESULTS]):
         print(f'\n' + ('#' * 10) + ' TEXT MATCH ' + ('#' * 10) + '\n')

    for idx, r in enumerate(RESULTS):
        
        if not sepatation_happened and r.get('type') == 'path_match':
            print(f'\n' + ('#' * 10) + ' PATH MATCH ' + ('#' * 10) + '\n')
            sepatation_happened = True
        print(f"{idx + 1})  {r.get('filename')}")

        
    while True:

        index = input('\n\nEnter a number or press "q" to go back : ')
        print('-' * len('Enter a number or press "q" to go back :  '))
        if index.strip().lower() == 'q':
            return

        try:
            parsed = int(index.lower().strip())
            break
        except:
            print('Invalid number, try again ...')
            continue
        

    open_file(RESULTS[parsed - 1].get('path'))
    
           

def open_file(path):
    program = "mousepad" if not is_windows_os else 'notepad.exe'

    subprocess.Popen([program, path]) 


main()

