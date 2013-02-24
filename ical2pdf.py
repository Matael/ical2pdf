#!/usr/bin/env python
# -*- coding:utf8 -*-

# File : ical2pdf.py
# Author : Mathieu (matael) Gaborit
#       <mathieu@matael.org>
# Date : Feb. 2013
# License : WTFPL
#
#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#                    Version 2, December 2004
#
# Copyright (C) 2004 Sam Hocevar <sam@hocevar.net>
#
# Everyone is permitted to copy and distribute verbatim or modified
# copies of this license document, and changing it is allowed as long
# as the name is changed.
#
#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
#
#  0. You just DO WHAT THE FUCK YOU WANT TO.
#

from __future__ import print_function
from icalendar import Calendar
from urllib import urlopen
from collections import namedtuple
from os import tempnam, system, getpid, remove

# fetch data

URL = "http://planning.univ-lemans.fr:8080/ade/custom/modules/plannings/anonymous_cal.jsp?resources=5810,5804&projectId=2&calType=ical&nbWeeks=4"
UTC_OFFSET = 1

print('Fetching ICAL file')

g = urlopen(URL)
gcal = Calendar.from_ical(g.read())

# sort events

print('Sorting events')

Vevent = namedtuple('Vevent', ['dtstart', 'dtend', 'summary', 'location'])

events = []
for component in gcal.walk():
    if component.name == "VEVENT":
        e = Vevent(dtstart=component.get('dtstart').dt,
                   dtend=component.get('dtend').dt,
                   summary=component.get('summary').encode('utf8'),
                   location=component.get('location').encode('utf8')
                  )
        events.append(e)

events.sort(key=lambda event: event.dtstart)

# Output



fn = 'ical2pdf'+str(getpid())+'.rst'
print('Generating ReST file (tempfile: ./'+fn)

fh = open(fn, 'w')

fh.write('===============\n')
fh.write('Emploi du Temps\n')
fh.write('===============\n\n')

previous_d = 0
for e in events:
    if previous_d != e.dtstart.date():
        l = len(str(e.dtstart.date()))
        fh.write('\n'+str(e.dtstart.date())+'\n'+'='*l+'\n')
        previous_d = e.dtstart.date()

    fh.write("- **[ "+e.location.capitalize().split(' ')[0]+" ] ")
    fh.write(str(e.dtstart.hour+UTC_OFFSET)+':'+str(e.dtstart.minute)+"**-"+str(e.dtend.hour+UTC_OFFSET)+':'+str(e.dtend.minute)+" ")
    fh.write(e.summary.capitalize()+'\n')

fh.close()

print('End of ReST output')
print('Compiling to PDF')

system('rst2pdf --output=./'+str(getpid())+'.pdf '+fn)

print('Removing temp file')
remove(fn)
