from django.contrib import admin

from .models import Monitor



def start_monitor(modeladmin, request, queryset):
    for c in queryset:
        c.start()
start_monitor.short_description = "Start selected monitors"

def stop_monitor(modeladmin, request, queryset):
    for c in queryset:
        c.stop()
stop_monitor.short_description = "Stop selected monitors"

def empty_collections(modeladmin, request, queryset):
    for c in queryset:
        c.delete()
empty_collections.short_description = "Remove all tweets from selected monitors"

class MonitorAdmin(admin.ModelAdmin):
    list_display = ('name','id','type','follow', 'track', 'is_running', 'exists', 'tweetcount')

    def is_running(self, obj):
        return obj.is_running()

    def exists(self, obj):
        return obj.exists()

    def tweetcount(self, obj):
        return obj.count()

    def get_actions(self, request):
        # Disable delete
        actions = super(MonitorAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return False

    is_running.boolean = True
    exists.boolean = True
    actions = [start_monitor, stop_monitor, empty_collections]


admin.site.register(Monitor,MonitorAdmin)
