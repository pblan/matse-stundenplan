from datetime import datetime, timedelta
import requests
import re
import os

def fetch_courses():
    now = datetime.now()

    start = "{}-09-01".format(now.year)
    end = "{}-08-30".format((now + timedelta(days=366)).year)

    url = "https://www.matse.itc.rwth-aachen.de/stundenplan/web/eventFeed/4?start={}&end={}".format(
        start, end)
    print(url)
    r = requests.get(url)
    dict = r.json()
    print("Got data...")
    
    print("Fetching courses...")
    s = set()
    for x in dict:
        if (re.search("Feiertag", x['title']) != None):
            continue
        s.add(x['title'])
    return s


