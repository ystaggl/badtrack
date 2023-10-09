#!/usr/bin/python3

from calendar import monthrange
import difflib
import os
import math
from pprint import pprint, pformat
import random
import os
import re
import time
import select
import sys
from termios import tcflush, TCIFLUSH
import smtplib
from uuid import uuid4
import inspect

from urllib.error import URLError
import urllib.request
from xml.etree import ElementTree as ET

from datetime import datetime, timedelta

week_days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

HTML_ENTITIES = re.compile('&[a-z]+;')
TABLE_RE = re.compile('<table.*?class=".*?schemaIndividual.*?>(.*?)</table>')
THEAD_RE = re.compile('<thead>.*?</thead>')
TR_RE = re.compile('<tr>*?<tr>')
BOOKED_TD_RE = re.compile('<td.*?class=".*?booked.*?".*?>')
SPACES_RE = re.compile('\s+')
ATTR_RE = re.compile('([^ ]+)="(.*?)"')

def format_seconds(s):
    minutes = math.floor(s / 60)
    remaining_seconds = s - minutes * 60
    return f'{minutes}m {remaining_seconds}s'

def store_init(path, now, date):
    def get_latest():
        file_names = sorted(
            (
                file_name
                for file_name in os.listdir(path)
                if file_name.startswith(date.strftime('%Y-%m-%d'))
            ),
            reverse=True)

        if len(file_names) == 0:
            return []

        latest, *rest = file_names

        with open(os.path.join(path, latest)) as f:
            return f.read().splitlines()

    def write_list(l):
        content = '\n'.join(l)
        with open(os.path.join(path, date.strftime('%Y-%m-%d') + '_at_' + now.strftime('%Y-%m-%d_%H:%M') + '.txt'), 'w') as f:
            f.write(content)

    return {
        'get_latest': get_latest,
        'write_list': write_list,
    }

def remove_thead(s):
    return THEAD_RE.sub('', s)

def remove_html_entities(s):
    return HTML_ENTITIES.sub('', s)

def remove_unmatched_tags(s):
    return s.replace('<div class="divHour">', '')

def get_datetime(year, month, day, *args):
    return datetime(year, month, 1, *args) + timedelta(day - 1)

assert get_datetime(2023, 2, 29) == datetime(2023, 3, 1)
assert get_datetime(2023, 2, 30) == datetime(2023, 3, 2)
assert get_datetime(2023, 12, 33) == datetime(2024, 1, 2)

def get_cache_key(d):
    return d.strftime('%Y-%m-%d')
    # return d.strftime('%Y-%m-%d_%H%M')

def get_cache(key):
    cache_file_path = os.path.join(os.environ['CACHE_FOLDER'], key)
    try:
        with open(cache_file_path, 'rb') as f:
            return f.read()
    except FileNotFoundError:
        return None

def set_cache(key, content):
    cache_file_path = os.path.join(os.environ['CACHE_FOLDER'], key)
    with open(cache_file_path, 'wb') as f:
        f.write(content)

def tag_to_dic(tag):
    return dict(ATTR_RE.findall(tag.lstrip('<td').rstrip('>').strip()))

def check_date(store, date_to_check, cache_exists):

    html = get_cache(get_cache_key(date_to_check))
    #development: enable caching
    #production: no caching

    if html is None:
        d = date_to_check
        req = urllib.request.Request(
            f'https://pba.yepbooking.com.au/ajax/ajax.schema.php?day={d.day}&month={d.month}&year={d.year}&id_sport=1')
        try:
            html = urllib.request.urlopen(req).read()
        except URLError as e:
            # Catch:
            # socket.gaierror: [Errno -5] No address associated with hostname
            print(e)
            print('Checking of ' + date_to_check.strftime('%Y-%m-%d') + ' has been skipped')
            return
        if cache_exists:
            set_cache(get_cache_key(date_to_check), html)
            print("Webpage cached")

    cleaned_html = remove_unmatched_tags(remove_html_entities(html.decode()))

    table_content = remove_thead(TABLE_RE.search(cleaned_html).group(1))

    rows = table_content.split('<tr')[1:] # First item is not a row containing td, because we split by <tr

    tr_list = (BOOKED_TD_RE.findall(row) for row in rows)

    rows_of_dic = (
        tuple({**tag_to_dic(td), 'court': i + 1} for td in cells)
        for i, cells in enumerate(tr_list)
    )

    booked_list = [
        '{date} Court {court}: {title}'.format(date=date_to_check.strftime('%d/%m %A'), **attrs)
        for row in rows_of_dic
        for attrs in row
        if row
    ]

    last = store['get_latest']()
    store['write_list'](booked_list)

    deletions = [ # This makes a list where each item is a string containing a booking that has been deleted.
        entry for group in (last[start:end]
            for op, start, end, *_b in difflib.SequenceMatcher(None, last, booked_list).get_opcodes() # We don't need bstart/bend if we're only getting deletions
            if op not in ('equal', 'insert')) # Only get deletions
        for entry in group # Flatten list
    ]

    if deletions:
        send_email(os.environ['EMAIL_HOST'],
                   int(os.environ['EMAIL_PORT']),
                   os.environ['EMAIL_USER'],
                   os.environ['EMAIL_PASSWORD'],
                   os.environ['EMAIL_FROM'],
                   os.environ['EMAIL_TO'],
                   "Deleted bookings:\n" + '\n'.join(deletions), # Pre-formatting the email to keep send_email generic
                   str(len(deletions)) + " deletions on " + date_to_check.strftime('%A %d/%m')) 


def send_email(email_host, email_port, user, password, email_from, email_to, email_body, email_subject):
    _user, email_domain = email_from.split('@', 1)
    email_text = inspect.cleandoc(f"""\
    Message-ID: <{uuid4()}@{email_domain}>
    From: Badminton Bookings <%s>
    To: %s
    Subject: %s

    %s
    """) % (email_from, email_to, email_subject, email_body) 
    try:
        smtp = smtplib.SMTP_SSL if email_port == 465 else smtplib.SMTP
        smtp_server = smtp(email_host, email_port)
        smtp_server.ehlo()

        if email_port == 465:
            smtp_server.login(user, password)

        smtp_server.sendmail(email_from, email_to, email_text.encode('UTF-8'))
        smtp_server.close()
        print ("Email sent successfully!")
    except Exception as ex:
        print ("Something went wrong….",ex)
    return

def run_loop(history_folder):
    cache_file_path = os.path.join(os.environ['CACHE_FOLDER'])
    cache_exists = os.path.exists(cache_file_path)

    while True:
        for i in range(7):
            wait_check_seconds = random.randint(3, 30) if i > 0 else 0
            time.sleep(wait_check_seconds)

            now = datetime.now()
            date = get_datetime(now.year, now.month, now.day + i, now.hour, now.minute)
            print('{2} Check for {1} (waited {0}s)' .format(wait_check_seconds, date.strftime('%a %d/%m'), now.strftime('%H:%M')))
            store = store_init(history_folder, now, date)
            check_date(store, date, cache_exists)

        minutes = lambda i: i * 60
        wait_seconds = random.randint(minutes(10), minutes(30))
        print('Wait {} after {}'.format(format_seconds(wait_seconds), datetime.now().strftime('%H:%M')))

        # sys.stdin will already start receiving keystrokes at the beginning of the programme
        # so an accidental Enter key press at the beginning of the programme will make the following
        # select.select code receive the keystroke skipping the while loop potentially multiple times
        # https://stackoverflow.com/questions/55525716/python-input-takes-old-stdin-before-input-is-called
        #tcflush(sys.stdin, TCIFLUSH)

        # Wait for input or timeout
        # https://stackoverflow.com/questions/1335507/keyboard-input-with-timeout
        #select.select([sys.stdin], [], [], wait_seconds)

        time.sleep(wait_seconds)

if __name__ == '__main__':
    try:
        run_loop(os.environ['HISTORY_FOLDER'])
    except KeyboardInterrupt:
        print('exit from keyboard interrupt')
