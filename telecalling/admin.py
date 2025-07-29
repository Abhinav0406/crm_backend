from django.contrib import admin
from .models import Assignment, CallLog, FollowUp

admin.site.register(Assignment)
admin.site.register(CallLog)
admin.site.register(FollowUp)
