from django.contrib import admin
from .models import KanbanBoard, Task, Timesheets, TimesheetSubmission
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


admin.site.register(KanbanBoard)
admin.site.register(Task)
admin.site.register(Timesheets)
admin.site.register(TimesheetSubmission)
