import calendar
import os
from datetime import datetime
from pathlib import Path

import pytz
import requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event

abbr_to_num = {name: num for num, name in enumerate(calendar.month_abbr) if num}

source = requests.get("https://auburn.edu/about/academic-calendar/")
soup = BeautifulSoup(source.content, "html.parser")

semester = soup.find_all("h2", {'class':"section-header"})
dates = soup.find_all("td", {'width':"25%"})
descriptions = soup.find_all("td", {'width':"55%"})

assert(len(dates) == len(descriptions))

sm_dict = {}

for sm in semester:
    sm_loc = str(soup).find(sm.text)
    sm_dict[sm.text] = sm_loc

cal = Calendar()

cal.add('prodid', 
        '-//Auburn University Calendar //www.auburn.edu/about/academic-calendar//')
cal.add('version', '2.0')


for i in range(len(dates)):
    dates_loc = str(soup).find(dates[i].text)
    cur_sm = sorted([sm for sm in sm_dict if sm_dict[sm] < dates_loc])[-1]
    year = str(cur_sm)[0:4]
   
    if (dates[i].text.find('-') != -1):
        start_date = dates[i].text[0:dates[i].text.find('-')].strip()
        end_date = dates[i].text[dates[i].text.find('-')+1:].strip()
        if end_date.isdigit():
            end_date = start_date[0:start_date.find(' ')] + ' ' + end_date
    else:
        start_date = dates[i].text
        end_date = dates[i].text

    event = Event()
    event.add('summary', descriptions[i].text)
    event.add('description', descriptions[i].text)
    event.add('dtstart',
              datetime(int(year), 
              abbr_to_num[start_date[0:start_date.find(' ')]], 
              int(start_date[start_date.find(' ')+1:]), 
              0, 0, 0, tzinfo=pytz.timezone('US/Central')))
    event.add('dtend', 
              datetime(int(year), 
              abbr_to_num[end_date[0:end_date.find(' ')]], 
              int(end_date[end_date.find(' ')+1:]), 
              0, 0, 0, tzinfo=pytz.timezone('US/Central')))
    cal.add_component(event)

directory = Path.cwd() 
if not directory.exists():
    os.makedirs(directory)

f = open(directory / 'AuburnCalendar.ics', 'wb')
f.write(cal.to_ical())
f.close()
