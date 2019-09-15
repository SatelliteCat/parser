from django.core.management.base import BaseCommand, CommandError
from parserLink.models import dbLog
import requests
from tqdm import tqdm
import math
from os.path import getsize
from datetime import datetime, tzinfo, timedelta


class Command(BaseCommand):
    args = '<link>'
    help = 'Parsing link from CLI\n Launch: python manage.py parserLink <link>'

    def handle(self, *args, **options):
        filename = self.download_file(*args)
        # self.parse_file(self.download_file(*args))
        # self.parse_file('access.log')
        self.parse_file(filename)

# Получение ссылки в качестве аргумента
    def add_arguments(self, parser):
        parser.add_argument(
            nargs=1,
            type=str,
            dest='args'
        )

    def download_file(self, url):
        """
        Сохранение данных, полученных по ссылке, в файл
        """
        local_filename = url.split('/')[-1]
        print(f'File name = {local_filename}')

        # Размер блока данных для загрузки
        block_size = 1024
        wrote = 0

        with requests.get(url, stream=True) as r:
            total_size = int(r.headers.get('content-length', 0))
            print(f'Total size = {total_size}')
            with open(local_filename, 'wb') as f:
                for data in tqdm(
                    r.iter_content(block_size),
                    total=math.ceil(total_size//block_size),
                    unit='MB',
                    unit_scale=True,
                    desc='Dowloading'
                ):
                    wrote = wrote + len(data)
                    f.write(data)

        if total_size != 0 and wrote != total_size:
            print("ERROR, something went wrong")

        return local_filename

    def parse_file(self, filename):
        month_map = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7,
                     'Aug': 8,  'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}

        with open(filename, 'r') as f:
            # total_size = sum(1 for _ in f)
            total_size = getsize(filename)
            t = tqdm(
                total=total_size,
                unit='MB',
                unit_scale=True,
                desc='Parsing'
            )
            for data in f.readlines():
                if data != '\n':
                    # Парсинг данных
                    split_line = data.split()
                    split_line_time = split_line[3][1:]
                    tz = FixedOffset(split_line[4][1:-1])
                    datetime_obj = datetime(year=int(split_line_time[7:11]),
                                            month=month_map[split_line_time[3:6]],
                                            day=int(split_line_time[0:2]),
                                            hour=int(split_line_time[12:14]),
                                            minute=int(split_line_time[15:17]),
                                            second=int(split_line_time[18:20]),
                                            tzinfo=tz)
                    # Создание объекта модели БД и сохранение данных В БД
                    obj = dbLog()
                    obj.ipAddress = split_line[0]
                    obj.dateLog = datetime_obj
                    obj.httpMethod = split_line[5][1:]
                    obj.uriLog = split_line[6]
                    obj.numError = int(split_line[8])
                    obj.sizeAnswer = int(
                        split_line[9]) if split_line[9] != '-' else None
                    obj.save()
                t.update(len(data))
            t.close()


class FixedOffset(tzinfo):
    """Преобразование часового пояса в datetime"""

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
