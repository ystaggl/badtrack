import difflib
import os
import math
from pprint import pprint
import random
import re
import time
import select
import sys
from termios import tcflush, TCIFLUSH

from urllib.error import URLError
import urllib.request
from xml.etree import ElementTree as ET

from datetime import datetime

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
    try:
        return datetime(year, month, day, *args)
    except ValueError:
        try:
            return datetime(year, month + 1, 1, *args)
        except ValueError:
            return datetime(year + 1, 1, 1, *args)

def get_cache_key(d):
    return d.strftime('%Y-%m-%d')
    return d.strftime('%Y-%m-%d_%H%M')

def get_cache(key):
    try:
        with open(key, 'rb') as f:
            return f.read()
    except FileNotFoundError:
        return None

def set_cache(key, content):
    with open(key, 'wb') as f:
        f.write(content)

def tag_to_dic(tag):
    return dict(ATTR_RE.findall(tag.lstrip('<td').rstrip('>').strip()))

def check_date(store, date_to_check):
    html = get_cache(get_cache_key(date_to_check))
    html = None

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

        set_cache(get_cache_key(date_to_check), html)

    cleaned_html = remove_unmatched_tags(remove_html_entities(html.decode()))

    table_content = remove_thead(TABLE_RE.search(cleaned_html).group(1))

    rows = table_content.split('<tr')[1:] # First item is not a row containing td, because we split by <tr

    tr_list = (BOOKED_TD_RE.findall(row) for row in rows)

    rows_of_dic = (
        tuple({**tag_to_dic(td), 'court': i + 1} for td in cells)
        for i, cells in enumerate(tr_list)
    )

    booked_list = [
        '{date} Court {court}: {title}'.format(date=date_to_check.strftime('%d/%m'), **attrs)
        for row in rows_of_dic
        for attrs in row
        if row
    ]

    last = store['get_latest']()
    store['write_list'](booked_list)

    diff = [
        '{}: {} -> {}'.format(op, last[astart:aend], booked_list[bstart:bend])
        for op, astart, aend, bstart, bend in  difflib.SequenceMatcher(None, last, booked_list).get_opcodes()
        if op != 'equal'
    ]

    if diff:
        pprint(diff)

def run_loop():
    while True:
        for i in range(7):
            wait_check_seconds = random.randint(3, 30) if i > 0 else 0
            time.sleep(wait_check_seconds)

            now = datetime.now()
            date = get_datetime(now.year, now.month, now.day + i, now.hour, now.minute)
            print('{2} Check for {1} (waited {0}s)' .format(wait_check_seconds, date.strftime('%a %d/%m'), now.strftime('%H:%M')))
            store = store_init('history/', now, date)
            check_date(store, date)

        minutes = lambda i: i * 60
        wait_seconds = random.randint(minutes(10), minutes(30))
        print('Wait {} after {}'.format(format_seconds(wait_seconds), datetime.now().strftime('%H:%M')))

        # sys.stdin will already start receiving keystrokes at the beginning of the programme
        # so an accidental Enter key press at the beginning of the programme will make the following
        # select.select code receive the keystroke skipping the while loop potentially multiple times
        # https://stackoverflow.com/questions/55525716/python-input-takes-old-stdin-before-input-is-called
        tcflush(sys.stdin, TCIFLUSH)

        # Wait for input or timeout
        # https://stackoverflow.com/questions/1335507/keyboard-input-with-timeout
        select.select([sys.stdin], [], [], wait_seconds)

try:
    run_loop()
except KeyboardInterrupt:
    print('exit from keyboard interrupt')
