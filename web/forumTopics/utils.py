from .models import Forums, Topics
import datetime
from django.template.loader import render_to_string

from django.conf import settings
from django.http import HttpResponseBadRequest,HttpRequest
from django.template import Context, loader
from django.utils.translation import gettext_lazy as _
import requests
import pytz
from email.message import EmailMessage
import aiosmtplib
from babel.dates import format_date
import tarfile
import os
import re

def generate_forums_pdf_template_as_string(request):

    request_date = request.GET.get('date', None)

    if request_date and isinstance(request_date, str):
        try:
            date = datetime.datetime.strptime(request_date, '%Y-%m-%d').date()
        except ValueError as e:
            return HttpResponseBadRequest(_('time data \"' + request_date + '\" does not match format \"YYYY-MM-DD\"'))
    else:
        today = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        local_tz = pytz.timezone(settings.TIME_ZONE)
        today = today.astimezone(local_tz)
        oneday = datetime.timedelta(days=1)
        yesterday = today - oneday
        date = yesterday.date()
    forumsList = Forums.objects.filter(isActive=True).order_by('id')
    topicDict = {}
    for forum in forumsList:
        topicsList = Topics.objects.filter(site_id=forum.id, datePost__date=date).order_by('datePost')
        topicDict[forum] = topicsList

    return render_to_string(request=request, template_name='forumTopics/forums_plain.html', context={'dateString': date.strftime('%d.%m.%Y'),
                                                      'topicDict': topicDict})

def pdf_as_file(path, date=None):
    request = HttpRequest()
    request.method = 'GET'
    if date:
        date_string = date.strftime('%Y-%m-%d')
        request.GET = {'date': date_string}
    request.META['SERVER_NAME'] = settings.DJANGO_HOST
    request.META['SERVER_PORT'] = settings.DJANGO_PORT
    html = generate_forums_pdf_template_as_string(request)
    try:
        pdf = requests.post(settings.PDF_GENERATOR_URL, data={'html': html}, timeout=10)
    except (requests.ConnectionError, requests.ReadTimeout) as e:
        return None
    with open(path,'wb') as file:
        file.write(pdf.content)
    return path


def archive_file(path):
    head, tail = os.path.split(path)
    output_filename = re.sub(r'.\w+$', '.tar.gz', tail)
    tar = tarfile.TarFile.gzopen(os.path.join(head, output_filename), mode='w', compresslevel=5)
    tar.add(path, arcname=os.path.basename(path))
    return os.path.join(head, output_filename)

def extract_file(path):
    tf = tarfile.open(path)
    tf.extractall()
    return re.sub(r'tar.gz', 'json', path)


async def send_mail_async(msg, recipients):

    """
    try to get queryset with async
    :param msg:
    :param recipients:
    :return:
    """

    if isinstance(recipients, list) and len(recipients) > 0:
        if settings.EMAIL_USE_TLS:
            await aiosmtplib.send(
                msg,
                hostname=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                use_tls=settings.EMAIL_USE_TLS,
                username=settings.EMAIL_HOST_USER,
                password=settings.EMAIL_HOST_PASSWORD,
                sender=settings.EMAIL_FROM,
                recipients=recipients
            )
        else:
            await aiosmtplib.send(
                msg,
                hostname=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                username=settings.EMAIL_HOST_USER,
                password=settings.EMAIL_HOST_PASSWORD,
                sender=settings.EMAIL_FROM,
                recipients=recipients
            )

def build_topics_mail(recipient, topics_count, attach_path=None):
    today = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    local_tz = pytz.timezone(settings.TIME_ZONE)
    today = today.astimezone(local_tz).date()
    oneday = datetime.timedelta(days=1)
    yesterday = today - oneday
    dateString = format_date(yesterday, format='long', locale='ru')
    host = settings.DJANGO_HOST
    port = settings.DJANGO_PORT
    if port != '80':
        url = 'http://' + host
    else:
        url = 'http://' + host


    topicsCountLastDigit = topics_count % 10
    review = 'отзывов'
    left = 'оставлено'
    if topicsCountLastDigit == 1:
        review = "отзыв"
        left = 'оставлен'
    elif topicsCountLastDigit in [2, 3, 4]:
        review = 'отзыва'

    if recipient.patronymic:
        fullName = recipient.firstName + ' ' + recipient.patronymic
    else:
        fullName = recipient.firstName
    t = loader.get_template('forumTopics/email.html')
    context = {'fullName': fullName, 'dateString': dateString,
               'url': url, 'topicsCount': topics_count, 'review': review, 'left': left, 'is_attach': True}
    html = t.render(context)

    context['is_attach'] = False
    html_no_attach = t.render(context)

    text = 'Здравствуйте, ' + fullName + '. За ' + dateString + \
           ' ' + left + ' ' + str(topics_count) + ' ' + review + \
           ' о Белтелеком. Информация в прикрепленном файле или по ссылке: ' + url
    text_no_attach = 'Здравствуйте, ' + fullName + '. За ' + dateString + \
                     ' ' + left + ' ' + str(topics_count) + ' ' + review + \
                     ' о Белтелеком. Информация по ссылке: ' + url
    subject = 'Отзывы о Белтелеком за ' + yesterday.strftime('%d.%m.%Y')

    msg = EmailMessage()
    msg['From'] = str(settings.WEATHER_EMAIL_FROM)
    msg['Subject'] = subject
    try:
        if attach_path:
            msg.set_content(text)
            msg.add_alternative(html, subtype='html')
            with open(attach_path, 'rb') as content_file:
                dir, filename = os.path.split(attach_path)
                content = content_file.read()
                msg.add_attachment(content, maintype='application', subtype='pdf', filename=filename)
        else:
            msg.set_content(text_no_attach)
            msg.add_alternative(html_no_attach, subtype='html')
    except FileNotFoundError:
        msg.set_content(text_no_attach)
        msg.add_alternative(html_no_attach, subtype='html')

    return msg
