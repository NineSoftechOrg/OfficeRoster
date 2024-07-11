from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group, AbstractUser, Permission
from django.core.serializers.json import DjangoJSONEncoder

# Create your models here.
User.add_to_class('role', models.CharField(max_length=50, choices=[
    ('admin', 'Admin'),
    ('user', 'User'),
    ('client', 'Client/Stakeholder'),
],default='user'))


class KanbanBoard(models.Model):
    Project_name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='board_create')
    assigned_users = models.ManyToManyField(User, related_name= 'assigned_boards', blank = False)

    def __str__(self):
        return self.Project_name


class Task(models.Model):
    board = models.ForeignKey(KanbanBoard, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status_choices = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('testing', 'Testing'),
        ('done', 'Done'),
    ]
    status = models.CharField(max_length=20, choices=status_choices)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False)
    order = models.PositiveIntegerField( blank=True)
    created_at = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    

class Timesheets(models.Model):
    title = models.CharField(max_length=150, null=True, blank=False)
    project_name = models.CharField(max_length=100, blank=True)
    date =  models.DateTimeField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    updated_date = models.DateField(auto_now_add=True, blank=True, null=True,)
    STATUS_CHOICES  = [
        ("Tobe_submitted", "To Be Submitted"),
        ("submitted", "Submitted"),
        ("Approved", "Approved"),
        ("rejected", "Rejected"),
    ]
    status = models.CharField(max_length=20, choices= STATUS_CHOICES , default=STATUS_CHOICES[0][0])
    submitted = models.BooleanField(blank=True, default=False)
    user = models.ForeignKey(User, on_delete= models.CASCADE, related_name="timesheets", null=True )
    
    def __str__(self):
        return self.title
    

class TimesheetSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="timesheet_submissions")
    month = models.IntegerField() 
    year = models.IntegerField()   
    submitted = models.BooleanField(default=False)
    created_date = models.DateField(auto_now_add=True, blank=True, null=True,)
    

    def __str__(self):
        return f"{self.user.username} - {self.month}/{self.year} - {self.created_date}"    
        