from django.shortcuts import render
from parserLink.models import dbLog
from django.db.models import Count, Q, Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import io
from django.http import HttpResponse
import xlsxwriter


def index(request):
    sizepage = 30  # Вывод 30 записей на одной странице основной таблицы
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

# Получение агрегированных данных
    num_unique_ip = message_list.distinct('ipAddress').count()
    queryset_ipAddress = message_list.values('ipAddress').annotate(
        Count('ipAddress')).order_by('-ipAddress__count')[:10]
    queryset_httpMethod = message_list.values('httpMethod').annotate(
        Count('httpMethod')).order_by('-httpMethod__count')
    sum_sizeAnswer = message_list.aggregate(Sum('sizeAnswer'))
    ipAddress_objects = queryset_ipAddress
    httpMethod_objects = queryset_httpMethod

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
    return render(request, "parserLink/index.html", {"message_list": message_list,
                                                     'findtext': findtext,
                                                     'last_question': last_question,
                                                     'num_unique_ip': num_unique_ip,
                                                     'ipAddress_objects': ipAddress_objects,
                                                     'httpMethod_objects': httpMethod_objects,
                                                     'sum_sizeAnswer': sum_sizeAnswer})


def export(request):

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
