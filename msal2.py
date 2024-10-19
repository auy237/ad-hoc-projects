from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def simple_get(url):
###
### Attempts to get the content at `url` by making an HTTP GET request.
### If the content-type of response is some kind of HTML/XML, return the
### text content, otherwise return None.
###
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
###
### Returns True if the response seems to be HTML, False otherwise.
###
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


def log_error(e):
   
### It is always a good idea to log errors. / 
### This function just prints them, but you can /
### make it do anything.

    print(f'could not find {e}')

def get_nba_tags():
    nba_team_html = simple_get('http://www.basketball-reference.com')
    nba_team_soup = BeautifulSoup(nba_team_html, 'html.parser')
    
    conf = ['E','W']
    nba_all = []
    for item in conf:
        nba_active = nba_team_soup.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']==f'confs_standings_{item}')

#        nba_active = nba_team_soup.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']==f'confs_standings_W') ### test line for correct table on main page

        nba_active_full = nba_active.find_all(lambda tag: tag.name=='th' and tag.has_attr('data-stat') and tag['data-stat']=='team_name')

        abr_list = []
        for row in nba_active_full[1:]:
            abr = row.a.text[0:]
            abr_list.append(abr)
        nba_all.append(abr_list)
    nba_teams = nba_all[0] + nba_all[1]   
    return nba_teams      



# extract team schedule
def get_nba_schedule(url,team,season):
    c_list = [url, team, season]
#    c_list = ['www.basketball-reference.com', 'MIN', '2019'] ##### TEST VALUES. MAKE SURE TO REPLACE WITH ACTUAL VARIABLE!!! ########
    for item in c_list:
        str(item)
#    team = 'MIN'    ##### Test step for adding home value to web list
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


        opp_abr = raw_html_parse.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=='games') ###this to pull abbreviations for team names
        opp_abr_team_html = opp_abr.find_all(lambda tag: tag.name=='td' and tag.has_attr('data-stat') and tag['data-stat']=='opp_name')
        opp_abr_list = []
        for item in opp_abr_team_html:
            ol2 = item.find('a')['href']
            opp_abr_list.append(ol2)
        opp_df = pd.DataFrame(opp_abr_list, columns=['team_html'])
        opp_df_breakout = opp_df['team_html'].str.split('/',expand=True)
        opp_df['team_abr'] = opp_df_breakout.iloc[:,2]
        opp_df['home_abr'] = team
        link_li_table = list(zip(opp_df['home_abr'], link_li_d, link_li_t, link_li_l, link_li_opp, opp_df['team_abr']))

#        print(link_li_table) ##### Step 2 Check 
#    return link_li_table   ##### Step 2     
        ########DATAFRAME HERE##########
        link_df = pd.DataFrame(link_li_table) 
        headers = link_df.columns = ['home_abr','date','time','location','opponent','opp_abr'] # renamed columns
                
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

        link_df_1 = link_df[link_df['location']==''].loc[:,['home_abr','opponent','opp_abr','weekday','date2','time']] ##### FINAL DATAFRAME #####

        test_n = []
        for n in range(len(link_df_1)):
            n += 1
            test_n.append(n)
        
        link_df_1['home_game_nm'] = test_n

#        print(link_df_1) ### validation step for final dataframe
        
        return link_df_1
    else:
        log_error(raw_html)


if __name__ == "__main__":
    import time
    site = 'www.basketball-reference.com'
    team_abr = get_nba_tags()
    year = str(input('Enter season: '))
    
    start = time.time()
    print('Retreiving team lists...')
    
    nba = []
    [nba.append(get_nba_schedule(site,item,year)) for item in team_abr]      
    
    nba_df = [pd.DataFrame(obj) for obj in nba]
    nba_con = pd.concat(nba_df)    

    end = time.time()
    print('time elapsed: % seconds' % (end - start))

 
    print(nba_con)    

    decision = ['y','n']

    while True:
        export = input("would you like to export this file? ('y' for yes/'n' for no) - ")  #export process

        
        if export == decision[0]:
            nba_con.to_csv(f'C:\\Users\\AUy\\Downloads\\nba schedule_{year}.csv', index_label='Reg Season Game #')
            print(f'saved to filepath C:\\Users\\AUy\\Downloads\\ as "nba schedule_{year}.csv"')
            print('END')
            break
        elif export == decision[1]:    
            print('file not saved')
            print('END')
            break
        elif export is None:
            print('Value must be entered. Please try again')
            export = None
        else:
            print('Value not recognized. Make sure to use lower case for "y" or "n" Please try again.')
            export = None                                               
        

        
        

