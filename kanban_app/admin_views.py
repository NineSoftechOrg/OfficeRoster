from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from .models import KanbanBoard, Task, Timesheets, TimesheetSubmission
from django.contrib import messages
from .forms import KanbanBoardForm, TaskForm
from .email_utils import send_project_assigned_email, send_newuser_register_email
from django.db.models import Max, F
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
import os, csv
import pandas as pd




def is_superadmin(user):
    return user.is_superuser or user.role in ['client', 'admin']

@login_required
@user_passes_test(is_superadmin)
def dashboard(request):
    if request.user.role == 'admin' or request.user.is_superuser:
        boards = KanbanBoard.objects.all()
        all_projects = []
        for project in boards:
            project_name = project.Project_name
            userids = list(project.assigned_users.values_list('username',flat=True))
            all_projects.append({project_name:userids})        
    else:
        boards= set()
        all_projects = KanbanBoard.objects.filter(assigned_users = request.user)
        for projects in all_projects:
            boards.add(projects)

    users = User.objects.all()
    context = {
        
        'users': users,
        'boards': boards,
        'all_projects':all_projects
    }
    return render(request, 'kanban_admin/dashboard.html', context)


@login_required  
@user_passes_test(is_superadmin)  
def create_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = User.objects.make_random_password(length=9, 
                           allowed_chars="abcdefghighlmpxy#@&$ABCDEFGHIJKLMNOPQRSTUVWSXZ1234567890") 
        role = request.POST.get('role')
        get_all_users_by_email = User.objects.filter(email=email)
        get_all_users_by_username = User.objects.filter(username=username)
        if get_all_users_by_username:
            messages.error(request, 'Error, Username already exists, Use another.')
            return redirect('create_user')
        if get_all_users_by_email:
            messages.error(request, 'Error, Email already exists, Use another.')
            return redirect('create_user')
        new_user = User.objects.create_user(username=username, email=email, password=password,role=role)
        new_user.save()
        user_data = {
            'username': username,
            'email': email,
            'password': password,
            'role': role
        }
        send_newuser_register_email((user_data))
        
        return redirect('dashboard')
    
    return render(request, 'kanban_admin/register_form.html', {})


@login_required
@user_passes_test(is_superadmin)
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.delete()
    return redirect('dashboard')   

@login_required
@user_passes_test(is_superadmin)
def board_detail(request, pk):
    board = get_object_or_404(KanbanBoard, pk=pk)
    tasks = board.tasks.all()
    statuses = ['todo', 'in_progress', 'testing', 'done']
    context = {
        'board': board,
        'tasks': tasks,
        'statuses': statuses,
    }
    return render(request, 'kanban_admin/board_detail.html', context)

@login_required
@user_passes_test(is_superadmin)
def admin_task_status_update(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        new_status = request.POST.get('new_status')

        task = get_object_or_404(Task, id=task_id)
        task.status = new_status
        task.save()
    return JsonResponse({'success': True})


@login_required
@user_passes_test(is_superadmin)
def board_create(request):
    if request.method == 'POST':
        form = KanbanBoardForm(request.POST)
        if form.is_valid():
            kanban_board = form.save(commit=False)
            kanban_board.created_by = request.user
            kanban_board.save()
            assigned_users = form.cleaned_data['assigned_users']
            kanban_board.assigned_users.set(assigned_users)
       
        #email sending
            send_project_assigned_email(kanban_board.Project_name, assigned_users)
           
            return redirect('dashboard')
    else:
        form = KanbanBoardForm()
    return render(request, 'kanban_admin/board_form.html', {'form': form})
  

@login_required
@user_passes_test(is_superadmin)
def board_update(request, pk):   
    board = get_object_or_404(KanbanBoard, pk=pk)
    if request.method == 'POST':
        form = KanbanBoardForm(request.POST, instance=board)
        if form.is_valid():
            
            #email sending
            current_assigned_users = set(board.assigned_users.all())
            board = form.save(commit=False)
            assigned_users = form.cleaned_data['assigned_users']
            board.assigned_users.set(assigned_users)
            board.save()
            new_assigned_users = set(assigned_users)-current_assigned_users
            if new_assigned_users:           
                send_project_assigned_email(board.Project_name, new_assigned_users)
            return redirect('dashboard')
    else:
        form = KanbanBoardForm(instance=board)
    return render(request, 'kanban_admin/board_form.html', {'form': form})


@login_required
@user_passes_test(is_superadmin)
def board_delete(request, pk):
    board = get_object_or_404(KanbanBoard, pk=pk)
    board.delete()
    return redirect('dashboard')


@login_required
def users_submitted_timeseets(request, ):
    
    timesheets_submitted = TimesheetSubmission.objects.filter(submitted = True).order_by('created_date')
    # users_submitted = {}
    
    # for submission in timesheets_submitted:
    #     if submission.user not in users_submitted:
    #         users_submitted[submission.user] = submission
    # users_submitted = list(users_submitted.values())

    # timesheet = Timesheets.objects.filter(status= )
    # status = request.GET.get('status') 
    # users = User.objects.all()
    return render(request, 'kanban_admin/users_submitted_timesheet_.html', {'timesheets_submitted': timesheets_submitted})


@login_required
@user_passes_test(is_superadmin)
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'kanban_admin/task_detail.html', {'task': task})
    
@login_required
@user_passes_test(is_superadmin)
def import_tasks_csv(request, board_id):
    if request.method == "POST":
        excel_file = request.FILES["excel_file"]
        fs = FileSystemStorage()
        filename = fs.save(excel_file.name, excel_file)
        # uploaded_file_url = fs.url(filename)
       
        file_path = fs.path(filename)
        try:
            if excel_file.name.endswith('.csv'):
                worksheet = pd.read_csv(file_path)
            else:
                worksheet = pd.read_excel(file_path, engine='openpyxl')

        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            messages.error(request, f'Invalid file format. Allowed file csv')   #validation
            return redirect(reverse('board_detail', args=[board_id]))
        
        required_columns = ['Title', 'Description', 'Status', 'Assigned To']
        for column in required_columns:
            if column not in worksheet.columns:
                if os.path.exists(file_path):
                    os.remove(file_path)
                messages.error(request, f'Missing required column/word format: {column}')  #validation
                return redirect(reverse('board_detail', args=[board_id]))
        
        for _,row in worksheet.iterrows():
            board = KanbanBoard.objects.get(id=board_id)
            try:
                assigned_to = board.assigned_users.get(username=row['Assigned To'])
            except User.DoesNotExist:
                if os.path.exists(file_path):
                 os.remove(file_path)
                messages.error(request, f'Assigned username does not exist in current Project.') #validation
                return redirect(reverse('board_detail', args=[board_id]))
            
            max_order = Task.objects.filter(board=board).aggregate(Max('order'))['order__max']
            order = 1 if max_order is None else max_order + 1
            tasks = Task(
                board=board,
                title=row['Title'],
                description=row['Description'],
                status=row['Status'],
                assigned_to=assigned_to,
                order=order
            )
            tasks.save()

        # Clean up the file after processing
        if os.path.exists(file_path):
            os.remove(file_path)

        return redirect(reverse('board_detail', args=[board_id]))
    return redirect(reverse('board_detail', args=[board_id]))


def export_task_csv(request, board_id):
    board = KanbanBoard.objects.get(id=board_id)
    response = HttpResponse(content_type = 'text/csv')
    response['Content-Disposition'] =f'attachment; filename="Project_{board.Project_name}_tasks.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Order', 'Title', 'Description', 'Status', 'Assigned To'])
    
    project_tasks = Task.objects.filter(board=board).values('order', 'title', 'description', 'status', assigned_to_name=F('assigned_to__username'))
    for task in project_tasks:
        writer.writerow([task['order'], task['title'], task['description'], task['status'], task['assigned_to_name']])
    return response


@login_required
@user_passes_test(is_superadmin)
def task_create(request, board_id):
    board = get_object_or_404(KanbanBoard, pk=board_id)
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.board = board
            max_order = Task.objects.filter(board=board).aggregate(Max('order'))['order__max']
            task.order = 1 if max_order is None else max_order + 1
            # task.order = Task.objects.filter(board=board).count() +  1
            task.save()
            return redirect('board_detail', pk=board_id)
        else:
            print(form.errors)
    else:
        form = TaskForm(initial={'board': board.id})
    form.fields['assigned_to'].queryset = board.assigned_users.all()
    return render(request, 'kanban_admin/task_form.html', {'form': form, 'board': board})


@login_required
@user_passes_test(is_superadmin)
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('board_detail', pk=task.board.pk)
    else:
        form = TaskForm(instance=task)
    form.fields['assigned_to'].queryset = task.board.assigned_users.all()
    return render(request, 'kanban_admin/task_form.html', {'form': form, 'task': task})


@login_required
@user_passes_test(is_superadmin)
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    board_id = task.board.pk
    task.delete()
    return redirect('board_detail', pk=board_id)
