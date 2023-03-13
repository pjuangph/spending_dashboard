from glob import glob
import os
from applecard import AppleStatementRead
    
directories = glob("./*/", recursive = True)
root_dir = os.path.abspath(os.curdir)
for d in directories:
    os.chdir(d)
    statements = glob('*.pdf')
    for s in statements:
        print(f'processing {s}')
        if "apple" in s.lower():
            df = AppleStatementRead(s)
            print('check')
    os.chdir(root_dir)
