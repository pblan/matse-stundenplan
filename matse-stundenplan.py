from datetime import datetime, timedelta
import re
import requests
import uuid
import os
import pytz

courses_dict = {'Betriebswirtschaftslehre': 'bwl',
                'C#': 'csharp',
                'Technisches Englisch': 'technisches_englisch',
                'Software Development in a Customer-Supplier Relation': 'sd_in_a_csr',
                'Fortran': 'fortran',
                'Einführung in die stochastischen Prozesse': 'einfuehrung_stoch_prozesse',
                'Prozessorientiertes Qualitätsmanagement (TÜV)': 'tuev',
                'C++': 'cpp',
                'Machine Learning': 'machine_learning',
                'Numerik 2': 'numerik_2',
                'Einführung in die Parallelprogrammierung': 'einfuehrung_parallelprogrammierung'}

tz = 'Europe/Berlin'

# Input: 2020-09-03T11:30:00
# Output: 20200903093000Z

def is_dst(dt=None, timezone=tz):
    if dt is None:
        dt = datetime.utcnow()
    timezone = pytz.timezone(timezone)
    timezone_aware_date = timezone.localize(dt, is_dst=None)
    return timezone_aware_date.tzinfo._dst.seconds != 0

def adjust_json_date(date, offset = -1):
    year, month, day, hour, minute, sec = date[0:4], date[5:7], date[8:10], int(date[11:13]), date[14:16], date[17:19]
    if (is_dst(datetime(int(year), int(month), int(day), hour, int(minute)))):
        hour -= 1
    hour += offset
    if (hour < 10):
        hour_str = "0{}".format(hour)
    else:
        hour_str = hour

    return "{}{}{}T{}{}{}Z".format(year, month, day, hour_str, minute, sec)


def adjust_datetime_date(date, offset = -1):
    year, month, day, hour, minute, sec = date.year, date.month, date.day, date.hour, date.minute, date.second
    hour += offset

    if (month < 10):
        month_str = "0{}".format(month)
    else:
        month_str = month

    if (day < 10):
        day_str = "0{}".format(day)
    else:
        day_str = day

    if (hour < 10):
        hour_str = "0{}".format(hour)
    else:
        hour_str = hour

    if (minute < 10):
        minute_str = "0{}".format(minute)
    else:
        minute_str = minute

    if (sec < 10):
        sec_str = "0{}".format(sec)
    else:
        sec_str = sec

    return "{}{}{}T{}{}{}Z".format(year, month_str, day_str, hour_str, minute_str, sec_str)


def build(id, name=None):
    print("Chosen calendar: ", id, " ", name)
    print("Starting to build new .ics file...")

    now = datetime.now()

    start = "{}-09-01".format(now.year)
    end = "{}-08-30".format((now + timedelta(days=366)).year)

    url = "https://www.matse.itc.rwth-aachen.de/stundenplan/web/eventFeed/{}?start={}&end={}".format(
        id, start, end)
    r = requests.get(url)
    dict = r.json()
    print("Got data...")

    str_list = []
    str_list.append('BEGIN:VCALENDAR\r\n')
    str_list.append('VERSION:2.0\r\n')
    str_list.append('METHOD:PUBLISH\r\n')
    str_list.append('PRODID:-//pblan/calendar/matse\r\n')
    str_list.append('CALSCALE:GREGORIAN\r\n')
    str_list.append('X-WR-TIMEZONE:{}\r\n'.format(tz))

    for x in dict:
        if ("Feiertag" in x['title']):
            continue
        if (name != None and name not in x['title']):
            continue

        # Create ICS/iCalendar events
        str_list.append('BEGIN:VEVENT\r\n')
        str_list.append('DTSTART:{}\r\n'.format(adjust_json_date(x['start'])))
        str_list.append('DTEND:{}\r\n'.format(adjust_json_date(x['end'])))
        str_list.append('DTSTAMP:{}\r\n'.format(adjust_datetime_date(now)))
        str_list.append('UID:{}\r\n'.format(str(uuid.uuid4())))
        str_list.append('CREATED:{}\r\n'.format(adjust_datetime_date(now)))
        str_list.append('DESCRIPTION:{}\r\n'.format(x['information']))
        str_list.append('LAST-MODIFIED:{}\r\n'.format(adjust_datetime_date(now)))
        str_list.append('SEQUENCE:0\r\n')
        # str_list.append('RRULE:FREQ=YEARLY;INTERVAL=1')
        str_list.append('SUMMARY:{}\r\n'.format(x['title']))
        str_list.append('LOCATION:{}\r\n{} {}\r\n{}\r\n'.format(
            x['location']['name'], x['location']['street'], x['location']['nr'], x['location']['desc']))
        str_list.append('TRANSP:TRANSPARENT\r\n')
        str_list.append('END:VEVENT\r\n')

    str_list.append('END:VCALENDAR')

    # Output ICS File
    if (name == None):
        calendar_path = os.path.expanduser("~") + '/html/dev/matse/{}/calendar.ics'.format(id)
    else:
        calendar_path = os.path.expanduser("~") + '/html/dev/matse/{}/{}_calendar.ics'.format(id,courses_dict(name))
    
    with open(calendar_path, 'wb') as f:
        content = ''.join(str_list)
        content = re.sub(r"None", "", content)
        content = re.sub(r"<br />", r"\r\n \\n", content)
        content = re.sub(r" +", " ", content)
        content = re.sub(r"\r\n\s*\r\n", "\r\n", content)
        
        b = content.encode('utf-8')
        f.write(b)
        print(os.path.realpath(f.name))

    print("Done writing data!")

def fetch_courses():
    now = datetime.now()

    start = "{}-09-01".format(now.year)
    end = "{}-08-30".format((now + timedelta(days=366)).year)

    url = "https://www.matse.itc.rwth-aachen.de/stundenplan/web/eventFeed/4?start={}&end={}".format(
        start, end)
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

#build(1)
#build(2)
#build(3)
for course in fetch_courses():
    build(4,course)