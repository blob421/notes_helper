NOTES HELPER
====================

Description :
-----------------

A simple script meant to help me find my notes quickly.

- Searches for words in files 
- Matches folders and file names


File naming convention:
------------------------------------
Separated by underscores and spaces:

- Os and sys.md (works)
- os.txt        (works)
- os_and_sys.md (works)
- os_and sys.md (works)


Separated by dots or dashes:

- os.sys.txt       (ignored)
- os_ and .sys.txt (ignored)
- os-and-sys.md    (ignored)

Starting with numbers:

- 0_import.txt     (comes first)
- imports.md       (comes second)
 
Search query examples: 
-------------------------------------

2 words (first word matches a folder name, second matches a filename, dirname or a word in a file): 

- python asyncio
- javascript promise 
- kubernetes minikube

1 word (matches a filename, a folder or a word in a file):

- asyncio 
- kubernetes 

