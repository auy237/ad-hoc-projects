# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 16:58:57 2019

@author: AUy
"""

from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from collections import OrderedDict

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
    
    
#def get_mls_icon():
mls_html = simple_get('https://www.espn.com/soccer/table/_/league/usa.1')
mls_soup = BeautifulSoup(mls_html, 'lxml')

#    mls_name = mls_soup.find(lambda tag: tag.name=='div' and tag.has_attr('id') and tag['id']=='fittPageContainer')
mls_body = mls_soup.find('tbody')
mls_team = mls_body.find_all('img')
mls_image_link = mls_body.find_all(lambda tag: tag.name=='img' and tag.has_attr('srcset'))
mls_abr = mls_body.find_all(lambda tag: tag.name=='abbr' and tag.has_attr('data-clubhouse-uid'))


abr = [] #abbreviation list
for i in mls_abr:
    abr_i = i.get_text()
    abr.append(abr_i)

team_name = [] #Full team name
for item in mls_team:
    team = item.get('alt')
    team_name.append(team)
    
image_link = [] #image link
for item in mls_image_link:
    image = item.get('href')
    image_link.append(image)
image_link_u = list(OrderedDict.fromkeys(image_link))


preframe = {'Team Name':team_name,'Abbreviation':abr,'Image Link':image_link_u}
mls_df = pd.DataFrame(preframe, columns=['Team Name','Abbreviation'])
split_img = mls_df['Image Link'].str.rsplit('/',2)   
 
image_id = [] #image ID
for row in split_img:
    name = row[-1]
    i = row[-2]
    image_id.append(i)

mls_df['image ID'] = image_id #new column

new_image_link = []
for i in mls_df['image ID']:
    image_link_str = f"https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/{i}.png&amp;h=40&amp;w=40 2x"
    new_image_link.append(image_link_str)
mls_df['Image Link'] = new_image_link

   
#def loop_html(var,ref):
#    new_list = []
#    for item in var:
#        content = item.get(ref)
#        new_list.append(content)
#    return new_list




    