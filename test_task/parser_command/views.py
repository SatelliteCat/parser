import io

import xlsxwriter
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from parser_command.models import Log


class IndexView(View):
    last_question = '?'

    def get(self, request, *args, **kwargs):
        """
        Обработка данных отображения главной страницы
        """

        # Получение основной таблицы
        message_list = self.get_main_table(request)

        # Агрегация
        num_unique_ip, ip_address_objects, http_method_objects, sum_size_answer = self.get_agr_data(
            message_list)
        message_list = self.pagination(
            request, message_list)  # Работа с пагинацией

        # Передача данных на страницу html
        return render(request, "parser_command/index.html", {"message_list": message_list,
                                                             'last_question': self.last_question,
                                                             'num_unique_ip': num_unique_ip,
                                                             'ip_address_objects': ip_address_objects,
                                                             'http_method_objects': http_method_objects,
                                                             'sum_size_answer': sum_size_answer})

    def pagination(self, request, message_list):
        """
        Пагинация
        """

        sizepage = 30  # Вывод 30 записей на одной странице основной таблицы
        paginator = Paginator(message_list, sizepage)
        page = request.GET.get('page')
        try:
            message_list = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            message_list = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            message_list = paginator.page(paginator.num_pages)
        return message_list

    def get_agr_data(self, message_list):
        """
        Получение агрегированных данных
        """

        with transaction.atomic():
            num_unique_ip = message_list.distinct('ip_address').count()
            queryset_ip_address = message_list.values('ip_address').annotate(
                Count('ip_address')).order_by('-ip_address__count')[:10]
            queryset_http_method = message_list.values('http_method').annotate(
                Count('http_method')).order_by('-http_method__count')
            sum_size_answer = message_list.aggregate(Sum('size_answer'))
        return num_unique_ip, queryset_ip_address, queryset_http_method, sum_size_answer

    def get_main_table(self, request):
        """
        Получение информации модели в зависимости от поиска
        """

        # findtext = request.POST.get('search')
        # question = request.GET.get('search')
        findtext = request.GET.get('search')

        if findtext is not None:
            # if question is not None:
            #     findtext = question
            message_list = Log.objects.filter(
                Q(ip_address__iexact=findtext) |
                Q(date_log__iexact=findtext) |
                Q(http_method__iexact=findtext) |
                Q(uri_log__iexact=findtext) |
                Q(num_error__iexact=findtext) |
                Q(size_answer__iexact=findtext)
            )
            self.last_question += f'search={findtext}&'
        else:
            message_list = Log.objects.all()
        return message_list

    def export(self):
        """
        Экспорт данных в XLSX-формате
        """

        # Create an in-memory output file for the new workbook.
        output = io.BytesIO()

        # Even though the final file will be in memory the module uses temp
        # files during assembly for efficiency. To avoid this on servers that
        # don't allow temp files, for example the Google APP Engine, set the
        # 'in_memory' Workbook() constructor option as shown in the docs.
        workbook = xlsxwriter.Workbook(
            output, {'remove_timezone': True, 'in_memory': False})
        worksheet = workbook.add_worksheet()

        # message_list = self.get_main_table(request)
        message_list = Log.objects.all()
        # Write some data.
        for row_num, obj in enumerate(message_list):
            # for col_num, cell_data in enumerate(obj):
            worksheet.write(row_num, 0, obj.ip_address)
            worksheet.write(row_num, 1, obj.date_log)
            worksheet.write(row_num, 2, obj.http_method)
            worksheet.write(row_num, 3, obj.uri_log)
            worksheet.write(row_num, 4, obj.num_error)
            worksheet.write(row_num, 5, obj.size_answer)

        # Close the workbook before sending the data.
        workbook.close()

        # Rewind the buffer.
        output.seek(0)

        # Set up the Http response.
        filename = 'log_db.xlsx'
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response
