from django.contrib import admin

from .models import Monitor


def start_monitor(modeladmin, request, queryset):
    for c in queryset:
        c.start()
start_monitor.short_description = "Start selected collections"

def stop_monitor(modeladmin, request, queryset):
    for c in queryset:
        c.stop()
stop_monitor.short_description = "Stop selected collections"

class MonitorAdmin(admin.ModelAdmin):
    list_display = ('name','type','follow', 'track', 'is_running', 'exists')

    def is_running(self, obj):
        return obj.is_running()

    def exists(self, obj):
        return obj.exists()

    is_running.boolean = True
    exists.boolean = True
    actions = [start_monitor, stop_monitor]


admin.site.register(Monitor,MonitorAdmin)
