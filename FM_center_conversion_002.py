# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 15:55:04 2019

@author: AUy
"""

import os
import pandas as pd
import shutil
import numpy as np

#functions
def replace_all(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)
    return text

def myreplace1(s):
    for ch in [" 12:00:00.000 AM"]:
        s = s.replace(ch, "")
    return s

def myreplace2(s):
    for ch in ["'"]:
        s = s.replace(ch, "")
    return s

#change directory to main repository#
conversion_therapy = "C:\\Users\\AUy\\OneDrive - CPGPLC\\adhoc\\Field Museum\\Sales Data\\conversion therapy"
archive_asc = "C:\\Users\\AUy\\OneDrive - CPGPLC\\adhoc\\Field Museum\\Sales Data\\archive"   
nwd = os.chdir("C:\\Users\\AUy\\OneDrive - CPGPLC\\adhoc\\Field Museum\\Sales Data\\conversion therapy")

#look for file#
#get all files with .asc end
print('directory set...')
#write something with no .asc file extension in it
print('grabbing files...')
asc_names = []
for path, name, file_names in os.walk(os.getcwd()):
    try:
        asc_names += [file for file in file_names if file.endswith('.asc')]
    except:
        asc_names += [file for file in file_names if file.endswith('.ASC')]

ap_data = []
for name in asc_names:
    try:
        reader = pd.read_table(open(name, "r"), delimiter=',')
        ap_data.append(reader)
    except:
        reader = pd.read_table(open(name, "r"))
        ap_data.append(reader)
print('grab file step complete')
#finsihed dataset  
print('making dataset...')  
final_data = pd.concat(ap_data, ignore_index = True)

#format INV_DATE field
function_list = [myreplace1,myreplace2]

for row in function_list:
   final_data["INV_DATE"] = final_data["INV_DATE"].map(row)

# 
date_range2 = final_data['INV_DATE'].astype(str)  
date_range = final_data.iloc[:,0].unique()

max_date_range = date_range2.max().replace("/","-")
min_date_range = date_range2.min().replace("/","-")

#add check columns

final_data["Ext_sales"] = final_data["UNIT_PRC"] * final_data["QTY"]

final_data["duplicate_check"] = final_data[["SKU","TRANS_ID"]].apply(lambda x: ''.join(x),axis=1)

final_data = final_data.sort_values(by=["INV_DATE","TRANS_ID"], ascending=True)
print('dataset created and date values assigned')
####Use for search only!!!!                            
#search_data = final_data[final_data['SKU']=='X1780'] #use for search only!!!!
#####Use for search only!!!

#append to sourcefile
#must make contingency to revert back to backup incase of failure. Else, risk of duplicate rows!!!!!!!!!!
print('appending new data to sourcefile...')
from datetime import date
sourcefile = f"C:\\Users\\AUy\\OneDrive - CPGPLC\\adhoc\\Field Museum\\Sales Data\\{date.today().year}\\Finished\\sourcefile_parsed.csv"
sf_df = pd.read_csv(open(sourcefile, "r"), index_col = None)

refreshed_df = sf_df.append(final_data)

refreshed_df = refreshed_df[pd.notnull(refreshed_df["Ext_sales"])]
print('refresh complete')    
#view_df = pd.pivot_table(refreshed_df, values='EXT_PRC', index=['INV_DATE'], columns=['LOCATION'], aggfunc=np.sum)

#backup current sourcefile
print('backing up current sourcefile')
backup = "C:\\Users\\AUy\\OneDrive - CPGPLC\\adhoc\\Field Museum\\Sales Data\\Backups"
shutil.copyfile(sourcefile,f"{backup}\\sourfile_BACKUP_{max_date_range}.csv")

#conversion to .csv file#
print('saving appended dataset')
final_data.to_csv(f"C:\\Users\\AUy\\OneDrive - CPGPLC\\adhoc\\Field Museum\\Sales Data\\\
converted data\\Sales_data_{min_date_range}_to_{max_date_range}.csv", index = False)

#archive final dataset and document
print('archiving new sourcefile')
refreshed_df.to_csv(f"C:\\Users\\AUy\\OneDrive - CPGPLC\\adhoc\\Field Museum\\Sales Data\\\
{date.today().year}\\Finished_archive\\sourcefile_parsed_{max_date_range}.csv", index = False)

#overwrite current sourcefile
print('overwriting new sourcefile')
refreshed_df.to_csv(f"C:\\Users\\AUy\\OneDrive - CPGPLC\\adhoc\\Field Museum\\Sales Data\\\
{date.today().year}\\Finished\\sourcefile_parsed.csv", index = False)

#move conversion files to archive
print('moving .asc files to archive')
directory = os.listdir(conversion_therapy)

for item in directory: 
    shutil.move(item,archive_asc)
print('done')
print('END')




