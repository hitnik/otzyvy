from django.db import models
from django.db.models import Transform, Lookup
from django.db.models.fields import DateTimeField
from django.conf import settings


@DateTimeField.register_lookup
class MySQLDatetimeDate(Lookup):

    lookup_name = 'mysql_datetz'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return "DATE(CONVERT_TZ(%s,'+00:00','Europe/Minsk'))=%s" % (lhs,rhs), params

@DateTimeField.register_lookup
class MySQLDatetimeDate(Lookup):

    lookup_name = 'mysql_datetz_lt'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return "DATE(CONVERT_TZ(%s,'+00:00','Europe/Minsk'))<%s" % (lhs,rhs), params

@DateTimeField.register_lookup
class PSQLDateTimeDate(Lookup):
    lookup_name = 'psql_datetz'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        # return "DATE(((%s AT TIME ZONE 'UTC') AT TIME ZONE 'Europe/Minsk'))=%s" % (lhs, rhs), params
        return "timezone('Europe/Minsk', %s)::date=%s" % (lhs, rhs), params

@DateTimeField.register_lookup
class PSSQLDatetimeDateLT(Lookup):

    lookup_name = 'psql_datetz_lt'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return "DATE(((%s AT TIME ZONE 'UTC') AT TIME ZONE '" + settings.TIME_ZONE + "'))<%s" % (lhs, rhs), params

class Sites(models.Model):
    name =models.CharField(max_length=24, blank=False, null=False, default=None, verbose_name='Название сайта')
    short = models.CharField(max_length=2, blank=True, null=False, default='', verbose_name='Краткое название сайта')
    isActive = models.BooleanField(default=True, verbose_name='Активно')

    def __str__(self):
        return '%s' % self.name

    class Meta:
        verbose_name = "Сайт"
        verbose_name_plural = 'Сайты'

    def save(self, **kwargs):
        self.short=self.name[0:2]
        super(Sites, self).save()

class Forums(models.Model):
    site = models.ForeignKey(Sites, blank=False, null=True, default=None,
                           verbose_name='Название сайта',on_delete=models.SET_NULL)
    name = models.CharField(max_length=64, blank=False, null=False, default=None,
                                 verbose_name='Название ветки форума')
    url = models.CharField(max_length=128, blank=False, null=False, default=None, verbose_name="URL сайта")
    pages = models.IntegerField(blank=False, null=False, default=0,
                                        verbose_name='Скопировано страниц')
    pagesTotal = models.IntegerField(blank=False, null=False, default=0,
                                        verbose_name='Всего страниц')
    isActive = models.BooleanField(default=True, verbose_name='Активно')

    def __str__(self):
        return '%s' % self.name

    class Meta:
        verbose_name = "Ветка форума"
        verbose_name_plural = 'Ветки форумов'

class ForumUsers(models.Model):
    id = models.CharField(max_length=12, blank=False, null=False, default=None, primary_key=True, verbose_name='ID пользователя форума')
    name = models.CharField(max_length=32, blank=False, null=False, default=None, verbose_name='Имя пользователя')
    site = models.ForeignKey(Sites, blank=False, null=True, default=None,
                           verbose_name='Cайт',on_delete=models.SET_NULL)

    def __str__(self):
        return '%s' % self.name

    class Meta:
        verbose_name = "Пользователь форума"
        verbose_name_plural = 'Пользователи форума'

class Topics(models.Model):
    id = models.CharField(max_length=12, blank=False, null=False, default=None, primary_key=True, verbose_name='ID поста форума')
    user = models.ForeignKey(ForumUsers,blank=False, null=True, default=None,
                           verbose_name='Пользователь',on_delete=models.CASCADE)
    topicText = models.TextField(blank=False, null=False, default=None, verbose_name='Содержание поста')
    site = models.ForeignKey(Forums, blank=False, null=True, default=None,
                           verbose_name='Название ветки форума',on_delete=models.SET_NULL)
    datePost = models.DateTimeField(auto_now=False, verbose_name='Дата опубликования')
    dateModified = models.DateTimeField(auto_now=False, verbose_name='Дата сохранения')
    url = models.URLField(max_length=256, blank=True, null=True, default=None)
    def __str__(self):
        return '%s' % self.datePost

    class Meta:
        verbose_name = "Топик"
        verbose_name_plural = 'Топики'

class Employees(models.Model):
    lastName = models.CharField(max_length=64, blank=False, null=False, default=None,
                                 verbose_name='Фамилия')
    firstName = models.CharField(max_length=64, blank=False, null=False, default=None,
                                 verbose_name='Имя')
    patronymic = models.CharField(max_length=64, blank=True, null=True, default=None,
                                 verbose_name='Отчество')
    email = models.EmailField(blank=True, null=False, default=None,
                                 verbose_name='Email')
    isActive=models.BooleanField(default=True, verbose_name='Статус')

    def __str__(self):
        return '%s' % self.lastName

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = 'Сотрудники'