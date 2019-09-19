import sys
from datetime import datetime, timedelta, tzinfo

import requests
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import DataError
from tqdm import tqdm

from parser_command.models import Log


class Command(BaseCommand):
    args = '<link>'
    help = 'Parsing link from CLI\n Launch: python manage.py parser_command <link>'

    def handle(self, *args, **options):
        self.parse_file(*args)

# Получение ссылки в качестве аргумента
    def add_arguments(self, parser):
        parser.add_argument(
            nargs=1,
            type=str,
            dest='args'
        )

    def parse_file(self, url):
        """
        Получение данных, обработка и сохранение в БД
        """

        month_map = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7,
                     'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
        objects_list = []  # Массив объектов для одной транзакции
        size_transaction = 100  # Число объектов в транзакции

        with requests.get(url, stream=True) as req:
            total_size = int(req.headers.get('content-length', 0))
            print(f'Total size = {total_size}')
            t = tqdm(
                total=total_size,
                unit='MB',
                unit_scale=True,
                desc='Parsing'
            )
            for data in req.iter_lines(decode_unicode=True):
                # Парсинг данных
                split_line = (data).split()
                if len(split_line) > 0:
                    split_line_time = split_line[3][1:]
                    timezone = FixedOffset(split_line[4][1:-1])
                    datetime_obj = datetime(year=int(split_line_time[7:11]),
                                            month=month_map[split_line_time[3:6]],
                                            day=int(split_line_time[0:2]),
                                            hour=int(split_line_time[12:14]),
                                            minute=int(split_line_time[15:17]),
                                            second=int(split_line_time[18:20]),
                                            tzinfo=timezone)
                    # Создание объекта модели БД и сохранение данных В БД
                    obj = Log()
                    obj.ip_address = split_line[0]
                    obj.date_log = datetime_obj
                    obj.http_method = split_line[5][1:]
                    obj.uri_log = split_line[6]
                    obj.num_error = int(split_line[8])
                    obj.size_answer = int(
                        split_line[9]) if split_line[9] != '-' else None
                    objects_list += [obj]
                    if len(objects_list) == size_transaction:
                        try:
                            Log.objects.bulk_create(objects_list)
                        except DataError:
                            pass
                        del(objects_list)
                        objects_list = []

                t.update(sys.getsizeof(data))
            t.close()


class FixedOffset(tzinfo):
    """
    Преобразование часового пояса в datetime
    """

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
