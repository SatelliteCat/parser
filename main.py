
import requests
from tqdm import tqdm
import math
from os.path import getsize
from datetime import datetime, tzinfo, timedelta
import re
import pytz


"""
Given a string representation of a datetime in apache format (e.g.
"01/Sep/2012:06:05:11 +0000"), return the python datetime for that string, with timezone
"""
month_map = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7,
             'Aug': 8,  'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
# s = s[1:-1]

# tz_string = s[21:26]
# tz = FixedOffset(tz_string)

# obj = datetime(year=int(s[7:11]), month=month_map[s[3:6]], day=int(s[0:2]),
#                hour=int(s[12:14]), minute=int(s[15:17]), second=int(s[18:20]),
#                tzinfo=tz)


class FixedOffset(tzinfo):
    """Fixed offset in minutes east from UTC."""

    def __init__(self, string):
        if string[0] == '-':
            direction = -1
            string = string[1:]
        elif string[0] == '+':
            direction = +1
            string = string[1:]
        else:
            direction = +1
            string = string

        hr_offset = int(string[0:2], 10)
        min_offset = int(string[2:3], 10)
        min_offset = hr_offset * 60 + min_offset
        min_offset = direction * min_offset
        self.__offset = timedelta(minutes=min_offset)

    def utcoffset(self, dt):
        return self.__offset


filename = 'access.log'
with open(filename, 'r') as f:
    # total_size = sum(1 for _ in f)
    total_size = getsize(filename)

    for data in f.readlines():
        if data != '\n':
            split_line = data.split()
            print(split_line)
            a = split_line[3][1:]

            string_tz = split_line[4][:-1]
            print(string_tz)
            # string_tz = '+0100'
            hr_offset = int(string_tz[0:2], 10)
            min_offset = int(string_tz[2:3], 10)
            min_offset = hr_offset * 60 + min_offset
            tz = timedelta(minutes=min_offset)
            tz = FixedOffset(string_tz)
            # print(tz)

            # result = re.findall(r'\[(.*?)\]', data)
            # print(a[7:11])
            obj = datetime(year=int(a[7:11]), month=month_map[a[3:6]], day=int(a[0:2]),
                           hour=int(a[12:14]), minute=int(a[15:17]), second=int(a[18:20]),
                           tzinfo=tz)
            result = a
            print(obj)
