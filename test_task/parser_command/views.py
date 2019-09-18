import io

import xlsxwriter
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count, Q, Sum
from django.http import HttpResponse
from django.shortcuts import render

from parser_command.models import Log


def index(request):
    """
    Обработка данных отображения главной страницы
    """

    sizepage = 30  # Вывод 30 записей на одной странице основной таблицы
    findtext = request.POST.get('search')
    question = request.GET.get('q')
    last_question = '?'

# Получение информации модели в зависимости от поиска
    if request.method == "POST" or question is not None:
        if question is not None:
            findtext = question
        message_list = Log.objects.filter(
            Q(ip_address__iexact=findtext) |
            Q(date_log__iexact=findtext) |
            Q(http_method__iexact=findtext) |
            Q(uri_log__iexact=findtext) |
            Q(num_error__iexact=findtext) |
            Q(size_answer__iexact=findtext)
        )
        last_question += f'q={findtext}&'
    else:
        message_list = Log.objects.all()

# Получение агрегированных данных
    num_unique_ip = message_list.distinct('ip_address').count()
    queryset_ip_address = message_list.values('ip_address').annotate(
        Count('ip_address')).order_by('-ip_address__count')[:10]
    queryset_http_method = message_list.values('http_method').annotate(
        Count('http_method')).order_by('-http_method__count')
    sum_size_answer = message_list.aggregate(Sum('size_answer'))
    ip_address_objects = queryset_ip_address
    http_method_objects = queryset_http_method

# Работа с пагинацией
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

# Передача данных на страницу html
    return render(request, "parser_command/index.html", {"message_list": message_list,
                                                         'findtext': findtext,
                                                         'last_question': last_question,
                                                         'num_unique_ip': num_unique_ip,
                                                         'ip_address_objects': ip_address_objects,
                                                         'http_method_objects': http_method_objects,
                                                         'sum_size_answer': sum_size_answer})


def export(request):
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

    findtext = request.POST.get('search')
    question = request.GET.get('q')
    last_question = '?'

# Получение информации модели в зависимости от поиска
    if request.method == "POST" or question is not None:
        if question is not None:
            findtext = question
        message_list = dbLog.objects.filter(
            Q(ipAddress__iexact=findtext) |
            Q(dateLog__iexact=findtext) |
            Q(httpMethod__iexact=findtext) |
            Q(uriLog__iexact=findtext) |
            Q(numError__iexact=findtext) |
            Q(sizeAnswer__iexact=findtext)
        )
        last_question += f'q={findtext}&'
    else:
        message_list = dbLog.objects.all()

    # Write some test data.
    for row_num, obj in enumerate(message_list):
        # for col_num, cell_data in enumerate(obj):
        worksheet.write(row_num, 0, obj.ipAddress)
        worksheet.write(row_num, 1, obj.dateLog)
        worksheet.write(row_num, 2, obj.httpMethod)
        worksheet.write(row_num, 3, obj.uriLog)
        worksheet.write(row_num, 4, obj.numError)
        worksheet.write(row_num, 5, obj.sizeAnswer)

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
