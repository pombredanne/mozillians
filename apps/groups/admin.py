from django.contrib import admin

from models import Group


class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'steward', 'wiki', 'website', 'irc_channel']
    search_fields = ['name']
    raw_id_fields = ['steward']

admin.site.register(Group, GroupAdmin)
