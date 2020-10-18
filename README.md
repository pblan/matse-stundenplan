# matse-stundenplan

## Background
As of now, there is no proper export of the MATSE Stundenplan (https://www.matse.itc.rwth-aachen.de/stundenplan/web/index.html). Always having to check a specific website to keep up to date is annoying.

Not anymore! 

This script fetches the data given in the MATSE Stundenplan and creates a new ICS Calendar file. This file is then hosted on the links given below - to create a simple and convenient calendar import!

## Functionality
The script will fetch all the data of a given calendar and then creates a new ICS file.
A CRON job is used to renew the file every hour.

Note: Since different clients are polling at different intervals, it may happen that changes are not immediately visible on your side.
If changes don't show after 24h, please send an inquiry to `patrick [dot] blaneck [at] rwth-aachen [dot] de`

Tested with Python3.6 on CentOS Linux 7 (Core).

## Usage
To access the calendar, simply copy the URL below and paste it into your Calendar Client (e.g. Google Calendar, Apple Calendar, Outlook).

(Update: Go to https://paddel.xyz/matse/ for more information!)
