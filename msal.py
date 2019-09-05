# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 10:34:10 2019

@author: AUy
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 09:49:41 2019

@author: AUy
"""

from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(f'could not find {e}')


#extract team schedule
def get_nba_schedule(url,team,season):
    c_list = [url, team, season]
    c_list = ['www.basketball-reference.com', 'MIN', '2019']
    for item in c_list:
        str(item)
        
    raw_html = simple_get(f'http://{c_list[0]}/teams/{c_list[1]}/{c_list[2]}_games.html')
    if raw_html is not None:
        raw_html_parse = BeautifulSoup(raw_html, 'html.parser')
        link_str = raw_html_parse.select('td')  #make list      
#        print(link_str) ####Step 1 check      
        link_li_d, link_li_t, link_li_l, link_li_opp = [[] for i in range(4)] #make empty list
        link_list = [link_li_d, link_li_t, link_li_l, link_li_opp] #list of lists
        data_stat_name = ['date_game','game_start_time','game_location','opp_name'] #####!!!!! these are the indicators when filtering to the 'td' tag (e.g. <td> data-stat=''</td>))
        
        for item in range(len(link_list)):
            for td in link_str:
                if td['data-stat'] == data_stat_name[item]:
                    link_list[item].append(td.text)
        link_li_table = list(zip(link_li_d, link_li_t, link_li_l, link_li_opp))
        print('Retreiving list...')
#        print(link_li_table) ##### Step 2 Check 
#    return link_li_table   ##### Step 2     
        ########DATAFRAME HERE##########
        link_df = pd.DataFrame(link_li_table) 
        headers = link_df.columns = ['date','time','location','opponent'] # renamed columns
        
        #### DATE PARSING################
        link_df['date'].replace(' ','')
        link_df[['weekday','month_day','year']] = link_df['date'].str.split(',', expand=True) #split date column
        link_df['date_squish'] = link_df['date'].str.strip() # split month_day column
        
        ########## DATE MODIFICATION###################
        date_breakout = link_df['date'].str.split(' ', expand=True)
        headers_date_breakout = date_breakout.columns = ['weekday','month', 'day', 'year']
        date_breakout_weekday = date_breakout['weekday'].str.replace(',','') #remove comma in weekday
        date_breakout_day = date_breakout['day'].str.replace(',','') #remove comma in day
        date_breakout['weekday'] = date_breakout_weekday ##### add to date series ##### YOU CAN CONSOLIDATE THIS LINE
        date_breakout['day'] = date_breakout_day #### add to date series ##### YOU CAN CONSOLIDATE THIS LINE 
        date_breakout['date2'] = date_breakout['month'] + ' ' + date_breakout['day'] + ' ' + date_breakout['year']
        
        date_breakout['date2'] = [datetime.strptime(m, '%b %d %Y') for m in date_breakout['date2']]

        link_df['date2'] = date_breakout['date2']   # ADD TO DATAFRAME .
        
#        hm_gm_list = [row + 1 for row in link_df.iloc[:,0]]
        
#        link_df['hm_gm_index'] = link_df.reset_index() ####!!GIVES ERROR!!###### ValueError when trying to reset index to have home game count

        link_df_1 = link_df[link_df['location']==''].loc[:,['opponent','weekday','date2','time']] ##### FINAL DATAFRAME #####
        
#        return link_df_1
    else:
        log_error(raw_html)
    print(link_df_1)    

    decision = ['y','n']

    while True:
        export = input("would you like to export this file? Y/N - ")  #export process

        
        if export in decision[0]:
            link_df_1.to_csv(f'C:\\Users\\AUy\\Downloads\\{c_list[1]}_{c_list[2]}.csv')
            print(f'saved to filepath C:\\Users\\AUy\\Downloads\\ as "{c_list[1]}_{c_list[2]}.csv"')
            return
        elif export in decision[1]:    
            print('file not saved')
            return
            break
        else:
            print('Value not recognized. Please try again.')
            export = None
   
if __name__ == "__main__":
    site = 'www.basketball-reference.com'
    team = str(input('Enter team name:'))
    year = str(input('Enter season:'))
    get_nba_schedule(site,team,year)
######### LOOKUP DICTIONARY ##########
###### NBA #####
#team_html = simple_get('http://www.basketball-reference.com/teams/')
#team_soup = BeautifulSoup(team_html, 'html.parser')
#active_team = team_soup.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=='teams_active')
#active_full_team = active_team.findAll(lambda tag: tag.name=='th' and tag.has_attr('data-stat') and tag['data-stat']=='franch_name')
#
################
#
#
#
###################################### 
#
############ WORKSPACE BELOW #################
#
######################################
#    
#raw_html = simple_get('https://www.basketball-reference.com/teams/MIN/2019_games.html')
#html = BeautifulSoup(raw_html, 'html.parser')
#reg_table = html.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=='games')
#reg_rows = reg_table.findAll(lambda tag: tag.name=='td')
#
##if post season...
#post_table = html.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=='games_playoffs')
#if post_table is not None:
#    post_rows = post_table.findAll(lambda tag: tag.name=='td')
#
#
#link_str = html.select('td')  #make list
#link_li_d, link_li_t, link_li_l, link_li_opp = [[] for i in range(4)] #make empty list
#link_list = [link_li_d, link_li_t, link_li_l, link_li_opp] #list of lists
#data_stat_name = ['date_game','game_start_time','game_location','opp_name'] #####!!!!! these are the indicators when filtering to the 'td' tag (e.g. <td> data-stat=''</td>))
#
#for item in range(len(link_list)):
#    for td in link_str:
#        if td['data-stat'] == data_stat_name[item]:
#            link_list[item].append(td.text)
#link_li_table = list(zip(link_li_d, link_li_t, link_li_l, link_li_opp))
#
################ TABLE CREATION CONTINGENCY (YAY!!!, YOU WON'T HAVE TO USE THIS) ################
##for td in link_str:
##    if td['data-stat'] == 'date_game':
##        link_li_d.append(td.text)
##    if td['data-stat'] == 'game_start_time':
##        link_li_t.append(td.text)
##    if td['data-stat'] == 'game_location':
##        link_li_l.append(td.text)    
##    if td['data-stat'] == 'opp_name':
##        link_li_opp.append(td.text)
##link_table = list(zip(link_li_d, link_li_t, link_li_l, link_li_opp))
#################################################################################################
#
#
#
#
#########DATAFRAME HERE##########
#link_df = pd.DataFrame(link_li_table) 
#headers = link_df.columns = ['date','time','location','opponent'] # renamed columns
#
##### DATE PARSING################
#link_df['date'].replace(' ','')
#link_df[['weekday','month_day','year']] = link_df['date'].str.split(',', expand=True) #split date column
#link_df['date_squish'] = link_df['date'].str.strip() # split month_day column
#
########### DATE MODIFICATION###################
#date_breakout = link_df['date'].str.split(' ', expand=True)
#headers_date_breakout = date_breakout.columns = ['weekday','month', 'day', 'year']
#date_breakout_weekday = date_breakout['weekday'].str.replace(',','') #remove comma in weekday
#date_breakout_day = date_breakout['day'].str.replace(',','') #remove comma in day
#date_breakout['weekday'] = date_breakout_weekday ##### add to date series
#date_breakout['day'] = date_breakout_day #### add to date series
#date_breakout['date2'] = date_breakout['month'] + ' ' + date_breakout['day'] + ' ' + date_breakout['year']
#
#date_breakout['date2'] = [datetime.strptime(m, '%b %d %Y') for m in date_breakout['date2']]
#
#
##ex_rep = link_df['date'].replace(',','')
##ex_date = []
##for m in link_df['date']:
##    m_change = datetime.strptime(m,'%c')
##    ex_date.append(m_change)
#
###################################################
#
#################TIME PARSE########################
#time_breakout = link_df['time'].str.split('p', expand=True) #### all times are EST
#time_date_breakout = time_breakout.columns = ['time','AM/PM']
###################################################
#
#
#
#link_df['date2'] = date_breakout['date2']   # ADD TO DATAFRAME 
#link_df['time2'] = time_breakout['time'] + 'PM' #### defunct. should probably remove (you hoarder....)
#
#link_df['hm_gm_index'] = link_df.index + 1
#
#link_df_1 = link_df[link_df['location']==''].loc[:,['opponent','weekday','date2','time']]
#
#
### small function to filter out away games
##def not_away(td):
##    return td and not (td.parent.string == '@')
##away = html.find_all(string=not_away)
##########################################
        

        
        

