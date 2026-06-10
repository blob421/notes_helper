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

FILES = ()
PATH_MATCHES = []
TEXT_MATCHES = []

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
    global FILES, PATH_MATCHES, TEXT_MATCHES
 
    PATH_MATCHES = []
    TEXT_MATCHES = []

   
    FILES = tuple(
        os.path.join(root, f)
        for root, _, files in os.walk(CONFIG.get('path'))
        for f in files
        if f.endswith('.md') or f.endswith('.txt')
    )         
  


def search_inputs():
    global FILES, PATH_MATCHES, TEXT_MATCHES
    PATH_MATCHES = []
    TEXT_MATCHES = []

    string = input('\nSearch (e.g. python core) : ').strip().lower()
    split_str = string.split(" ")
    while True:
        try:
            for path in FILES:
                with open(path, 'r') as f:
                    content = f.read().strip().lower()
                    filtered_text = re.sub(r'[,:\.]', '', content)
                    words = filtered_text.split()

                    sub_path = re.sub(rf'(^{re.escape(CONFIG.get("path"))})(.+)', r'\2', path)
                    subbed_path = sub_path.lower()
                    root = sub_path.split(path_separator)[0]
                    split_path = subbed_path.split(path_separator)

                    file_name = split_path[-1].split('.')[0]
                    
                    filename_tokens = get_filename_tokens(file_name)
                    if not filename_tokens:
                        continue
          
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
        return
    


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
            return

        try:
            parsed = int(index.lower().strip())
            break
        except:
            print('Invalid number, try again ...')
            continue
        
    if parsed > len(TEXT_MATCHES):

        open_file(PATH_MATCHES[(parsed - len(TEXT_MATCHES)) - 1].get('path'))

    else:
        open_file(TEXT_MATCHES[parsed - 1].get('path'))
    
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

