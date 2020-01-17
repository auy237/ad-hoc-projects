# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 13:33:27 2019

@author: AUy
"""

def move_file():
    import os
    
    root = "C:\\Users\\SClemente\\Desktop"
    nwd = f"{root}\\FQ invoice sales"
    
    #write something with no .asc file extension in it
    file_names = []
    for path, name, file_names in os.walk(root):
        try:
            file_names += [file for file in file_names if file.endswith('DIIS.xls')]
        except:
            file_names += [file for file in file_names if file.endswith('DIIS.XLS')]
    
    if file_names is None:
        for item in file_names:
            os.shutil(item,nwd)
    else:
        print("No files found")