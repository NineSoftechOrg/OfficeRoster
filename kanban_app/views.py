from django.shortcuts import render, redirect, get_object_or_404
from .models import KanbanBoard, Task
from .forms import TaskUserForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse


def welcome(request):
    '<h1> Welcome to the page </h2>'
    return redirect('login')

# def register(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         # if len(password) < 3:
#         #     messages.error(request, 'Password must be at least 3 characters')
#         #     return redirect('register')
#         get_all_users_by_username = User.objects.filter(username=username)
#         if get_all_users_by_username:
#             messages.error(request, 'Error, username already exists, Use another.')
#             return redirect('register')

#         new_user = User.objects.create_user(username=username, email=email, password=password)
#         new_user.save()

#         messages.success(request, 'User successfully created, login now')
#         return redirect('login')
#     return render(request, 'todoapp/register.html', {})


@csrf_exempt
def loginpage(request):
    if request.method == 'POST':
        username = request.POST.get('uname')
        password = request.POST.get('pass')

        validate_user = authenticate(username=username, password=password)
        if validate_user is not None:
            login(request, validate_user)
            if validate_user.is_superuser or validate_user.role in ['client','admin']:
                return redirect('dashboard')
            else:
                return redirect('user_dashboard')
        else:
            messages.error(request, 'Error, wrong user details or user does not exist')
            return redirect('login')
    return render(request, 'todoapp/login.html', {})


@login_required
def user_dashboard(request):
    return render(request, 'kanban/userdashboard.html' )

@login_required
def project_list(request):
    boards= set()
    projects_list = KanbanBoard.objects.filter(assigned_users = request.user)
    for projects in projects_list:
        boards.add(projects)
    context = {
        'boards': boards,
    }
    
    return render(request, 'kanban/project_list.html', context)
    
  
#board = projet
#board_id = project_id
@csrf_exempt
@login_required
def kanban_board(request, board_id): 
    board = get_object_or_404(KanbanBoard, id= board_id)
    if request.method == 'POST':
        task_title = request.POST.get('task')
        task_description = request.POST.get('description')
        
        if task_title:
            if task_title:
                max_order_task = Task.objects.filter(board=board).order_by('-order').first()
                new_order = max_order_task.order + 1 if max_order_task else 1
            
            Task.objects.create(
                board=board,
                title=task_title,
                description=task_description,
                status='todo',  
                assigned_to=request.user,
                order = new_order  #Task.objects.filter(board=board).order_by('-order').first().order + 1
            )
            return redirect(reverse('kanban_board', args=[board_id]))

    tasks = Task.objects.filter(board=board, assigned_to=request.user)
    statuses = ['todo', 'in_progress', 'testing', 'done']
    context = {
        'board': board,
        'tasks': tasks,
        'statuses': statuses,
    }
    
    return render(request, 'kanban/board.html', context)


@csrf_exempt
@login_required
def update_task_status(request):
    task_id = request.POST.get('task_id')
    new_status = request.POST.get('new_status')
    
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
    task.status = new_status
    task.save()
    
    return JsonResponse({'success': True})

    # task = get_object_or_404(Task, pk=task_id, assigned_to=request.user) 
    # if request.method == 'POST':
    #     form = TaskUserForm(request.POST, instance=task)
    #     if form.is_valid():
    #         form.save()
    #         return redirect('kanban_board', board_id=task.board.id)  
    #     else:
    #         return render(request, 'kanban/user_task_form.html', {'form': form, 'task': task})
    # else:
    #     form = TaskUserForm(instance=task)
    # context ={ 'task': task,
    #            'form': form,
    # }
    # return render(request, 'kanban/user_task_form.html', context) 
        

def logout_view(request):
    logout(request)
    return redirect('login')