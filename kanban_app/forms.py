from django import forms
from .models import KanbanBoard, Task, Timesheets
from django.contrib.auth.models import User


class KanbanBoardForm(forms.ModelForm):
    class Meta:
        model = KanbanBoard
        fields = ['Project_name', 'assigned_users']

def save(self, commit=True):
        instance = super(KanbanBoardForm, self).save(commit=False)
        if not instance.pk:  
            instance.created_by = self.current_user
        if commit:
            instance.save()
        return instance


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'assigned_to']


class TaskUserForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['assigned_to'].disabled = True
            self.fields['order'].disabled = True
            self.fields['board'].disabled = True

class TimesheetsForm(forms.ModelForm):
    class Meta:
        model = Timesheets
        fields= '__all__'

        
