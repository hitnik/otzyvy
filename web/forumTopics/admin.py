from django.contrib import admin
from .models import *

class SitesAdmin(admin.ModelAdmin):
    list_display = ('name', 'isActive',)
    list_filter = ('isActive',)
    list_editable = ('isActive',)
    readonly_fields = ('id',)
    ordering = ['id']

    class Meta:
        model =Sites

admin.site.register(Sites, SitesAdmin)



class ForumsAdmin(admin.ModelAdmin):
    list_display =('name','site', 'pages', 'pagesTotal', 'isActive')
    ordering = ['site','id']
    list_filter = ('isActive',)
    list_editable = ('isActive',)
    readonly_fields = ('name', 'url', 'pages', 'pagesTotal')


    def make_enabled(self, request, queryset):
        rows_updated = queryset.update(isActive=True)
        if rows_updated == 1:
            message_bit = "1 запись активирована"
        else:
            message_bit = "%s записей были активированы" % rows_updated
        self.message_user(request, "%s" % message_bit)
    make_enabled.short_description = "Сделать активными"

    def make_disabled(self, request, queryset):
        rows_updated=queryset.update(isActive=False)
        if rows_updated == 1:
            message_bit = "1 запись отключена"
        else:
            message_bit = "%s записей были отключены" % rows_updated
        self.message_user(request, "%s" % message_bit)
    make_disabled.short_description = "Отключить"

    actions = [make_enabled, make_disabled]

    class Meta:
        model =Forums

# admin.site.add_action(ForumsAdmin.make_enabled, 'make_enabled')
# admin.site.add_action(ForumsAdmin.make_disabled, 'make_disabled')
admin.site.register(Forums, ForumsAdmin)



class ForumUsersAdmin(admin.ModelAdmin):
    list_display = ('name','id', 'site')
    class Meta:
        model =ForumUsers

admin.site.register(ForumUsers, ForumUsersAdmin)



class TopicsAdmin(admin.ModelAdmin):
    list_display =('id','user','datePost', 'dateModified')
    ordering = ['datePost',]
    list_filter = ('datePost',)
    readonly_fields = ('id', 'user', 'topicText', 'datePost', 'dateModified', 'url')


    class Meta:
        model =Topics

admin.site.register(Topics, TopicsAdmin)

class EmployeesAdmin(admin.ModelAdmin):
    list_display = ('lastName','firstName', 'patronymic', 'email','isActive')
    ordering = ['lastName']
    list_filter = ('isActive',)
    list_editable = ('isActive',)

    def make_enabled(self, request, queryset):
        rows_updated = queryset.update(isActive=True)
        if rows_updated == 1:
            message_bit = "1 запись активирована"
        else:
            message_bit = "%s записей были активированы" % rows_updated
        self.message_user(request, "%s" % message_bit)
    make_enabled.short_description = "Сделать активными"

    def make_disabled(self, request, queryset):
        rows_updated=queryset.update(isActive=False)
        if rows_updated == 1:
            message_bit = "1 запись отключена"
        else:
            message_bit = "%s записей были отключены" % rows_updated
        self.message_user(request, "%s" % message_bit)
    make_disabled.short_description = "Отключить"

    actions = [make_enabled, make_disabled]

    class Meta:
        model =Employees



admin.site.register(Employees, EmployeesAdmin)