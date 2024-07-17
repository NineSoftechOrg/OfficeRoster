from django.contrib import admin
from .models import KanbanBoard, Task, Timesheets, TimesheetSubmission
from django.contrib.auth.admin import UserAdmin
from import_export import resources
from django.contrib.auth.models import User

class TaskResource(resources.ModelResource):
    class Meta:
        model =  Task
        fields = ['order', 'title', 'description', 'status', 'assigned_to' ]
        export_order = ('order', 'title', 'description', 'status', 'assigned_to') 

#board , created_at

admin.site.register(KanbanBoard)
admin.site.register(Task)
admin.site.register(Timesheets)
admin.site.register(TimesheetSubmission)


    
     