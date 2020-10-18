from datetime import datetime, timedelta
import re
import requests
import uuid
import os
import pytz
import hashlib
import db_handler
import sys

YEAR_DICT = {'1': '1. Lehrjahr',
             '2': '2. Lehrjahr',
             '3': '3. Lehrjahr',
             '4': 'Wahlpflicht'
}

COURSES_DICT = {'Mathematische Grundlagen': 'mathe_grundlagen',
                'Vorstellung der Sozialberatung': 'sozialberatung',
                'Klausureinsicht [1. Lehrjahr]': 'klausureinsicht_1',
                'Klausureinsicht [2. Lehrjahr]': 'klausureinsicht_2',
                'Klausureinsicht [3. Lehrjahr]': 'klausureinsicht_3',
                'Klausureinsicht [Wahlpflicht]': 'klausureinsicht_3',
                'Termine Umweltschutz- und Arbeitssicherheitsseminare': 'umweltschutz',
                'Java-Blockkurs': 'java_block',
                'Wahl des Semestersprechers': 'semestersprecher',
                'Selbstlernphase für asynchrone Videovorlesung [Analysis 1]': 'ana1_async',
                'Selbstlernphase für asynchrone Videovorlesung [Lineare Algebra 1]': 'la1_async',
                'Selbstlernphase für asynchrone Videovorlesung [Java]': 'java_async',
                'Selbstlernphase für asynchrone Videovorlesung [Stochastik]': 'sto_async',
                'Selbstlernphase für asynchrone Videovorlesung [Softwaretechnik]': 'swt_async',
                'Java-Blockkursklausur': 'java_block_klausur',
                'Erstievent': 'erstievent',
                'IT-Grundlagen': 'it_grundlagen',
                'Kenntnistest': 'kenntnistest',
                'Tutorium Java': 'tutorium_java',
                'Übung 1. Lehrjahr': 'uebung_1',
                'Übung 2. Lehrjahr': 'uebung_2',
                'Datenbanken': 'db',
                'Softwaretechnik': 'swt_sync',
                'SWT-Messe': 'swt_messe',
                'Stochastik': 'sto_sync',
                'IHK-Zwischenprüfung': 'ihk_zwischenpruefung',
                'IHK-Abschlussprüfung': 'ihk_abschlusspruefung',
                'Prüfungsvorbereitung': 'pruefungsvorbereitung',
                'Betriebswirtschaftslehre': 'bwl',
                'C#': 'csharp',
                'Technisches Englisch': 'technisches_englisch',
                'Software Development in a Customer-Supplier Relation': 'sd_in_a_csr',
                'Fortran': 'fortran',
                'Einführung in die stochastischen Prozesse': 'einfuehrung_stochastische_prozesse',
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

def add_event(calendar, event, name, now = datetime.now()):
    if ("Feiertag" in event['title']):
        return
    if (name != None and event['title'] not in name):
        return
    if ("[" in name and "Lehrjahr" not in name and re.sub(r"<br />*\s*", "", event['information']) not in name):
        return
    if ("lausur" in name and "lausur" not in event['title']):
        return

    # Create ICS/iCalendar events
    calendar.append('BEGIN:VEVENT\r\n')
    calendar.append('DTSTART:{}\r\n'.format(adjust_json_date(event['start'])))
    calendar.append('DTEND:{}\r\n'.format(adjust_json_date(event['end'])))
    calendar.append('DTSTAMP:{}\r\n'.format(adjust_datetime_date(now)))
    calendar.append('UID:matse-{}-{}\r\n'.format(COURSES_DICT[name], adjust_json_date(event['start'])))
    calendar.append('CREATED:{}\r\n'.format(adjust_datetime_date(now)))
    calendar.append('DESCRIPTION:{}\r\n'.format(event['information']))
    calendar.append('LAST-MODIFIED:{}\r\n'.format(adjust_datetime_date(now)))
    calendar.append('SEQUENCE:0\r\n')
    calendar.append('SUMMARY:{}\r\n'.format(event['title']))
    calendar.append('LOCATION:{}\r\n{} {}\r\n{}\r\n'.format(
        event['location']['name'], event['location']['street'], event['location']['nr'], event['location']['desc']))
    calendar.append('TRANSP:TRANSPARENT\r\n')
    calendar.append('END:VEVENT\r\n')

def build_calendar(id, name):
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
        add_event(str_list, x, name)

    str_list.append('END:VCALENDAR')

    # Output ICS File
    calendar_path = os.path.expanduser("~") + '/html/matse/calendars/{}_calendar.ics'.format(COURSES_DICT[name])

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
    
def fetch_courses(id):
    now = datetime.now()

    start = "{}-09-01".format(now.year)
    end = "{}-08-30".format((now + timedelta(days=366)).year)

    url = "https://www.matse.itc.rwth-aachen.de/stundenplan/web/eventFeed/{}?start={}&end={}".format(
        id, start, end)
    r = requests.get(url)
    dict = r.json()
    print("Got data...")
    
    print("Fetching courses...")
    s = set()
    for x in dict:
        if (re.search("Feiertag", x['title']) != None):
            continue
        
        if (re.search("Selbstlernphase für asynchrone Videovorlesung", x['title']) != None):
            s.add(x['title'] + " [" + re.sub(r"<br />*\s*", "", x['information']) + "]")
        elif (re.search("Klausureinsicht", x['title']) != None and id < 4):
            s.add(x['title'] + " [" + str(id) + ". Lehrjahr]")
        elif (re.search("Klausureinsicht", x['title']) != None and id == 4):
            s.add(x['title'] + " [Wahlpflicht]")
        else: 
            s.add(x['title'])
    return s

def trim_calendar(calendar):
    calendar_dir = os.path.expanduser("~") + '/html/matse/calendars/{}_calendar.ics'.format(calendar)
    calendar = []
    with open(calendar_dir) as f:
        calendar = f.readlines()
    return calendar[6:-1]

def combine_courses(user, courses):
    user_path = os.path.expanduser("~") + '/html/matse/calendars/{}'.format(user)
    if not os.path.exists(user_path):
        os.makedirs(user_path)
    user_path += '/calendar.ics'

    str_list = []
    str_list.append('BEGIN:VCALENDAR\r\n')
    str_list.append('VERSION:2.0\r\n')
    str_list.append('METHOD:PUBLISH\r\n')
    str_list.append('PRODID:-//pblan/calendar/matse\r\n')
    str_list.append('CALSCALE:GREGORIAN\r\n')
    str_list.append('X-WR-TIMEZONE:{}\r\n'.format(tz))

    for course in courses:
        calendar = trim_calendar(course)
        for line in calendar:
            str_list.append(line)
    
    str_list.append('END:VCALENDAR')
    with open(user_path, 'wb') as f:
        content = ''.join(str_list)
        b = content.encode('utf-8')
        f.write(b)
        print(os.path.realpath(f.name))

    print('Done writing courses {} for user {}!'.format(courses, user))
    return

def refresh_base():
    # Creating readable list of courses as .csv
    csv_columns = ['id', 'name', 'handle']
    csv_file = "courses.csv"
    csv_path = os.path.expanduser("~") + '/html/matse/{}'.format(csv_file)
    csv_str_list = []

    # Refreshing base calendars for each course
    for course in fetch_courses(1):
        if (course not in COURSES_DICT): print("### MISSING ENTRY: " + course)
        csv_str_list.append('{},{},{}\n'.format(YEAR_DICT['1'], course, COURSES_DICT[course]))
        build_calendar(1, course)

    for course in fetch_courses(2):
        if (course not in COURSES_DICT): print("### MISSING ENTRY: " + course)
        csv_str_list.append('{},{},{}\n'.format(YEAR_DICT['2'], course, COURSES_DICT[course]))
        build_calendar(2, course)
        
    for course in fetch_courses(3):
        if (course not in COURSES_DICT): print("### MISSING ENTRY: " + course)
        csv_str_list.append('{},{},{}\n'.format(YEAR_DICT['3'], course, COURSES_DICT[course]))
        build_calendar(3, course)
        
    for course in fetch_courses(4):
        if (course not in COURSES_DICT): print("### MISSING ENTRY: " + course)
        csv_str_list.append('{},{},{}\n'.format(YEAR_DICT['4'], course, COURSES_DICT[course]))
        build_calendar(4, course)

    with open(csv_path, 'wb') as f:
        content = ''.join(csv_str_list)
        
        b = content.encode('utf-8')
        f.write(b)
        print(os.path.realpath(f.name))

def refresh_user_calendars():
    # Refreshing calendars for each user 
    db = db_handler.database
    cursor = db.cursor()
    cursor.execute("SELECT hashUsers, coursesUsers FROM users WHERE coursesUsers!='' AND coursesUsers IS NOT NULL")
    results = cursor.fetchall()

    for result in results:
        hashed_name = result[0]
        courses = result[1].split(',')
        combine_courses(hashed_name, courses)

def run():
    refresh_base()
    refresh_user_calendars()
    