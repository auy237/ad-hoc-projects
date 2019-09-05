# -*- coding: utf-8 -*-
"""
Created on Tue Jan 15 09:23:33 2019

@author: auy
"""
def get_file():
    
    import os
    import pandas as pd
    import shutil
    from datetime import datetime
    
    def myreplace1(s):
        for ch in [" 12:00:00.000 AM"]:
            s = s.replace(ch, "")
        return s
    
    def myreplace2(s):
        for ch in ["'"]:
            s = s.replace(ch, "")
        return s
    
    #change directory to main repository#
    root = "C:\\Users\AUy\\OneDrive - CPGPLC\\adhoc\\Moda Center\\Datasets"    
    nwd = os.chdir(f"{root}\\conversion_therapy")
    
   
    #look for file#
    #get all files with .asc end
    asc_names = []
    for path, name, file_names in os.walk(os.getcwd()):
        try:
            asc_names += [file for file in file_names if file.endswith('.asc')]
        except:
            asc_names += [file for file in file_names if file.endswith('.ASC')]
    
    print(f'grabbing {len(asc_names)} file(s)...')
    ap_data = []
    for name in asc_names:
        reader = pd.read_table(open(name, "r"))
        ap_data.append(reader)
   
    print('file(s) grabbed')
    if ap_data is not None:
  
        final_data = pd.concat(ap_data, ignore_index = True)
        count = final_data["INV_DATE"].count()
        print(f'dataset created with {count} rows')  
        #format INV_DATE field
                
        function_list = [myreplace1,myreplace2] #use functions above to convert date field
        
        for row in function_list:
           final_data["INV_DATE"] = final_data["INV_DATE"].map(row)
                             
        max_date_range = max(final_data["INV_DATE"], key=lambda d: datetime.strptime(d, '%m/%d/%Y')).replace("/","-") #most recent date within .asc file
        
        print('converting .asc file to .csv...')
        #archive conversion to .csv file#
        try:
            final_data.to_csv(f"{root}\\csv_conversion\\SalesData_{max_date_range}.csv", index = False) #archive converted snapshot
            print('snapshot saved...')
            
            final_data.to_csv(f"{root}\\csv_FINAL\\SalesData_FINAL.csv", index = False)  #move to final source filepath
            print('sourcfile saved...')
           
            directory = os.listdir(nwd)
            for item in directory:
                shutil.move(item,f"{root}\\asc_archive\\salesdata_{max_date_range}.asc")  #move .asc file to archive directory
            print(f'final file converted and .asc file saved to "{root}\\asc_archive\\salesdata_{max_date_range}.asc"')
        except (SyntaxError, FileNotFoundError):
            print(f'error on conversion')
        
    else:
        print('error processing files. Please check if .asc file is in "conversion_therapy"')
    print('END...')
if __name__=="__main__":
    get_file()