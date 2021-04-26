from django_rq import job
from django.core import mail
from django.urls import reverse
from django.core.mail import EmailMessage, EmailMultiAlternatives
from .models import Employees, Topics, ForumUsers
import datetime
from django.conf import settings
from django.template import Context, loader
from babel.dates import format_date
import logging
import logging.config
from .utils import pdf_as_file
import os
import pytz
import asyncio
from .utils import build_topics_mail, send_mail_async


DICTLOGCONFIG={
"version":1,
        "handlers":{
            "fileHandler":{
                "class":"logging.FileHandler",
                "formatter":"myFormatter",
                "filename":"/usr/src/app/forumTopics/djhelpdeskclearDB.log"
            }
        },
        "loggers":{
            "clearDB":{
                "handlers":["fileHandler"],
                "level":"INFO",
            }
        },
        "formatters":{
            "myFormatter":{
                "format":"[%(asctime)s] - %(levelname)s - %(message)s"
            }
        }
}

@job
def sendmail():

    today = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    local_tz = pytz.timezone(settings.TIME_ZONE)
    today = today.astimezone(local_tz).date()
    oneday = datetime.timedelta(days=1)
    yesterday = today - oneday

    employees = Employees.objects.filter(isActive=True)
    if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.mysql':
        topicsCount = Topics.objects.filter(datePost__mysql_datetz=yesterday).count()
    else:
        topicsCount = Topics.objects.filter(datePost__date=yesterday).count()

    path = 'forums.pdf'
    try:
        os.remove(path)
    except FileNotFoundError:
        pass

    path = pdf_as_file(path)

    args_list = []

    for employee in employees:
        msg = build_topics_mail(employee, topicsCount, path)
        recipients = [employee.email]
        args_list.append({'msg': msg, 'recipients': recipients})

    async def run():
        await asyncio.gather(*(send_mail_async(i['msg'], i['recipients']) for i in args_list), return_exceptions=True)
    asyncio.run(run())


@job
def deleteOldTopics():
    logging.config.dictConfig(DICTLOGCONFIG)
    logger = logging.getLogger("clearDB")
    today = datetime.date.today()
    yearAgo = today
    yearAgo = yearAgo.replace(year=yearAgo.year - 1)
    if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.mysql':
        deleteCandidates = Topics.objects.filter(datePost__datetz_lt=yearAgo).defer('id', 'user_id')
    else:
        deleteCandidates = Topics.objects.filter(datePost__date_lt=yearAgo).defer('id', 'user_id')

    logger.info("%d candidates for deletion" % (len(deleteCandidates)))
    count = 0;
    for topic in deleteCandidates:
        userCount = Topics.objects.filter(user__id=topic.user_id).count()
        if userCount == 1:
            count += 1
            ForumUsers.objects.filter(id=topic.user_id).delete()
        else:
            Topics.objects.filter(id=topic.id).delete()
    logger.info("delete %d topics, %d forumUsers" % (len(deleteCandidates), count))

    fileName = DICTLOGCONFIG['handlers']['fileHandler']['filename']
    linesToWrite = []
    countLines = 0
    with open(fileName, 'r') as f:
        lines = f.readlines()
        for line in list(reversed(lines)):
            linesToWrite.append(line)
            countLines += 1
            if countLines > 100 : break
    with open(fileName, 'w') as f:
        for line in list(reversed(linesToWrite)):
            f.write(line)
