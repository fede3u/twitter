from django.contrib import admin

from .models import Monitor


def start_monitor(modeladmin, request, queryset):
    for c in queryset:
        c.start()
start_monitor.short_description = "Start selected collections"



class MonitorAdmin(admin.ModelAdmin):
    list_display = ('name','type','follow', 'track', 'locations')

    actions = [start_monitor]


admin.site.register(Monitor,MonitorAdmin)
