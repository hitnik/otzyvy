from django.apps import AppConfig
import django_rq
import datetime
from redis.exceptions import ConnectionError
from django.utils.timezone import pytz
from django.conf import settings


class ForumtopicsConfig(AppConfig):
    name = 'forumTopics'
    verbose_name = 'Топики форумов'


    def ready(self):
        """
         set datetime in utc for job schedule
        """
        date_now = datetime.datetime.utcnow()
        year = date_now.year
        month = date_now.month
        day = date_now.day
        timezone_local = pytz.timezone(settings.TIME_ZONE)

        date_schedule_sendmail = datetime.datetime.strptime(settings.SEND_MAIL_TIME, '%H:%M:%S')
        hour_sendmail = date_schedule_sendmail.hour
        minutes_sendmail = date_schedule_sendmail.minute
        seconds_sendmail = date_schedule_sendmail.second

        date_schedule_sendmail = datetime.datetime(year, month, day,
                                                   hour_sendmail, minutes_sendmail, seconds_sendmail)
        date_schedule_sendmail = timezone_local.localize(date_schedule_sendmail)
        date_schedule_sendmail = date_schedule_sendmail.astimezone(pytz.utc)

        date_schedule_clear = datetime.datetime.strptime(settings.CLEAR_OLD_TOPICS_TIME, '%H:%M:%S')

        hour_clear = date_schedule_clear.hour
        minutes_clear = date_schedule_clear.minute
        seconds_clear = date_schedule_clear.second

        date_schedule_clear = datetime.datetime(year, month, day,
                                                   hour_clear, minutes_clear, seconds_clear)
        date_schedule_clear = timezone_local.localize(date_schedule_clear)
        date_schedule_clear = date_schedule_clear.astimezone(pytz.utc)


        while date_schedule_sendmail <= datetime.datetime.utcnow().astimezone(pytz.utc):
            date_schedule_sendmail = date_schedule_sendmail + datetime.timedelta(seconds=settings.SEND_MAIL_INTERVAL)

        while date_schedule_clear <= datetime.datetime.utcnow().astimezone(pytz.utc):
            date_schedule_clear = date_schedule_clear + datetime.timedelta(seconds=settings.CLEAR_OLD_TOPICS_INTERVAL)


        from . import jobs

        try:
            scheduler = django_rq.get_scheduler('default')
            for job in scheduler.get_jobs():
                if job.func_name == 'forumTopics.jobs.sendmail':
                    job.delete()
                if job.func_name == 'forumTopics.jobs.deleteOldTopics':
                    job.delete()

            scheduler.schedule(scheduled_time=date_schedule_sendmail,
                               func=jobs.sendmail,
                               interval=settings.SEND_MAIL_INTERVAL, result_ttl=settings.SEND_MAIL_INTERVAL+300
                               )

            scheduler.schedule(scheduled_time=date_schedule_clear,
                               func=jobs.deleteOldTopics,
                               interval=settings.CLEAR_OLD_TOPICS_INTERVAL, result_ttl=settings.CLEAR_OLD_TOPICS_INTERVAL+300
                               )

            count_send_mail = 0
            count_deleteOldTopics = 0
            for job in scheduler.get_jobs():
                if job.func_name == 'forumTopics.jobs.sendmail':
                    count_send_mail += 1
                    if count_send_mail > 1:
                        job.delete()
                if job.func_name == 'forumTopics.jobs.deleteOldTopics':
                    count_deleteOldTopics += 1
                    if count_deleteOldTopics > 1:
                        job.delete()

        except ConnectionError:
            pass