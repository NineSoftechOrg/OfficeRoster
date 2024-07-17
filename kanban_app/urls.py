from django.urls import path

from .admin_views import  create_user, user_delete, task_create, task_detail, admin_task_status_update, task_update, task_delete, dashboard, board_detail, board_create, \
    users_submitted_timeseets, board_update, board_delete, export_task_csv, import_tasks_csv

from .views import  welcome, loginpage, user_dashboard, project_list, kanban_board, update_task_status, logout_view

from .timesheets_views import timesheet_dashboard, all_timesheets, add_timesheet, submit_timesheets, \
    delete_event, check_submission_status, admin_view_timesheets, api_timesheets, approve_timesheets, reject_timesheets, delete_timesheet_submitted

urlpatterns = [
    path('', welcome, name= 'welcome'),
    # path('register/', views.register, name='register'),
    path('login/', loginpage, name='login'),
    path('user_dashboard/', user_dashboard, name= "user_dashboard"),
    path('projects/', project_list, name='project_list'),
    path('projects/<int:board_id>/', kanban_board, name='kanban_board'), 
    path('timesheets_board/', timesheet_dashboard, name = "timesheet_dashboard"),
    path('all_timesheets/', all_timesheets, name='all_timesheets'), 
    path('delete_event/<int:timesheet_id>/', delete_event, name='delete_event'),
    path('add_timesheet/', add_timesheet, name='add_timesheet'),
    path('submit_timesheets/', submit_timesheets, name='submit_timesheets'),
    path('check_submission_status/', check_submission_status, name='check_submission_status'),
    path('usersubmiited_timeseets/', users_submitted_timeseets, name='users_submitted_timeseets'),
    path('admin/view_timesheets/<int:user_id>/<int:month>/<int:year>/', admin_view_timesheets, name='admin_view_timesheets'),
    path('api/user-timesheets/', api_timesheets, name='api_timesheets'),
    path('admin/approve-timesheets/', approve_timesheets, name='approve_timesheets'),
    path('admin/reject-timesheets/', reject_timesheets, name='reject_timesheets'),
    path('timesheet_submitted/<int:user_submitted_id>/',   delete_timesheet_submitted, name='delete_timesheet_submitted'),
    # path('get_timesheet_status/<int:user_id>/<int:month>/<int:year>/', get_timesheet_status, name="get_timesheet_status"),
    path('kanban/update_task_status/', update_task_status, name='update_task_status'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('board/new/', board_create, name='board_create'),
    path('create_user/new/', create_user, name='create_user'),
    path('user/<int:pk>/delete/', user_delete, name='user_delete'),
    path('board/<int:pk>/', board_detail, name='board_detail'),
    path('board/<int:pk>/edit/', board_update, name='board_update'),
    path('board/<int:pk>/delete/', board_delete, name='board_delete'),
    path('board/<int:board_id>/task/new/', task_create, name='task_create'),
    path('task/import_csv/<int:board_id>/', import_tasks_csv, name = "import_tasks_csv"),
    path('task/export_csv/<int:board_id>/', export_task_csv, name="export_task_csv" ),
    path('admin_task_status_update/', admin_task_status_update, name='admin_task_status_update'),
    path('task/<int:pk>/', task_detail, name='task_detail'),
    path('task/<int:pk>/edit/', task_update, name='task_update'),
    path('task/<int:pk>/delete/',   task_delete, name='task_delete'),

]
