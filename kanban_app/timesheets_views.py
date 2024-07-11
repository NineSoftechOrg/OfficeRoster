from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from .models import Timesheets, TimesheetSubmission
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from calendar import monthrange

@login_required
def timesheet_dashboard(request):
    all_timesheets = Timesheets.objects.filter(user = request.user)
    context = {
        'all_timesheets' :  all_timesheets,
    }
    return render(request, "timesheets/dashboard.html", context)


@login_required
def all_timesheets(request):
    start_param = request.GET.get('start')
    end_param = request.GET.get('end')
    if start_param and end_param:
        start_date = datetime.strptime(start_param, '%Y-%m-%d')
        end_date = datetime.strptime(end_param, '%Y-%m-%d')
        timesheets = Timesheets.objects.filter(user=request.user, date__range=[start_date, end_date])
    else:
        timesheets = Timesheets.objects.filter(user=request.user)
    timesheets_list = []
    for ts in timesheets:
        start_datetime = f"{ts.date.strftime('%Y-%m-%d')}T{ts.start_time.strftime('%H:%M:%S')}"
        end_datetime = f"{ts.date.strftime('%Y-%m-%d')}T{ts.end_time.strftime('%H:%M:%S')}"

        timesheets_list.append({
            "id": ts.id,
            "title": ts.title,
            "project_name":ts.project_name,
            "date": ts.date,
            "user": request.user.username,
            "start": start_datetime,
            "end": end_datetime,
            "status": ts.status,

        })
    return JsonResponse(timesheets_list, safe=False)

@csrf_exempt
@login_required
def add_timesheet(request):
    if request.method == 'POST':
        project_name = request.POST.get("project_name")
        title = request.POST.get("title", None)
        start_time = request.POST.get("start_time", None)
        end_time = request.POST.get("end_time", None)
        date = request.POST.get('selected_date')
        # updated_date = datetime.date.today
        # existing_timesheet = Timesheets.objects.filter(user = request.user, date=date, status='submitted').exists()
        # print(existing_timesheet, "EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEe")
        # if existing_timesheet:
            # return JsonResponse({"error": "Timesheet for this date has already been submitted and cannot be edited."}, status=403)
        try:
            timesheet  = Timesheets(
                project_name = project_name,
                title=title, 
                start_time=start_time, 
                end_time=end_time,
                date=date,
                user = request.user,
                # updated_date = updated_date,
                status = "Tobe_submitted",
                submitted=False

            )
            timesheet.save()
            return JsonResponse({"success": True})
        except Exception as e:
            print(e)
            return JsonResponse({"error": str(e)}, status=400)
            
    return JsonResponse({"error": "Invalid request method"}, status=405)


@login_required
@csrf_exempt
def delete_event(request, timesheet_id):
    if request.method == 'POST':
            timesheet = get_object_or_404(Timesheets, id=timesheet_id)
            timesheet.delete()
            return JsonResponse({'success': True, 'message': 'Timesheet deleted successfully.'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

@login_required
@csrf_exempt
def submit_timesheets(request):
    if request.method == "POST":
        current_year = int(request.POST.get('year'))
        current_month = int(request.POST.get('month'))
        start_date = datetime(current_year, current_month, 1)
        end_date = datetime(current_year, current_month, monthrange(current_year, current_month)[1])

        if TimesheetSubmission.objects.filter(user=request.user, year=current_year, month=current_month,
                                              submitted=True).exists():
            return JsonResponse(
                {'success': False, 'message': 'You have already submitted the timesheet for this month.'})

        #checking for missing timesheet dates
        missing_days = []
        for single_date in (start_date + timedelta(n) for n in range((end_date - start_date).days +1)):
            if not Timesheets.objects.filter(user=request.user, date=single_date).exists():
                missing_days.append(single_date.strftime('%Y-%m-%d'))
        
        if missing_days:
            return JsonResponse({'success': False, 'message': f'Make sure to fill Missing timesheets for the dates: {", ".join(missing_days)}'})

        #update timesheets to be 'submitted' 
        Timesheets.objects.filter(user=request.user, date__year=current_year, date__month=current_month).update(status ="submitted", submitted=True)   
        print(Timesheets.objects.filter(user=request.user, date__year=current_year, date__month=current_month).update(status ="submitted", submitted=True)  , "JJJJJJJJJJJJJJJJJJ")
        #marking the month as submitted
        TimesheetSubmission.objects.update_or_create(
            user=request.user,
            month = current_month,
            year= current_year,
            defaults={"submitted": True}
        ) 
        return JsonResponse({'sucess': True, 'message': 'All timesheets for this month have been submitted successfully.'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid Request Method.'})


@login_required
def check_submission_status(request):
   year = int(request.GET.get('year'))
   month = int(request.GET.get('month'))
   submitted_timesheets = Timesheets.objects.filter(
        user=request.user,
        date__year=year,
        date__month=month,
        submitted=True
    ).exists()
   
   return JsonResponse({'submitted': submitted_timesheets})


@login_required
def admin_view_timesheets(request, user_id, month, year):
    user = get_object_or_404(User, id=user_id)
    timesheets = Timesheets.objects.filter(user=user, date__year=year, date__month=month, status='submitted')

    return render(request, 'kanban_admin/timesheets_view.html', {
        'user': user,
        'timesheets': timesheets,
        'month': month,
        'year': year
    })

@login_required
@csrf_exempt
def delete_timesheet_submitted(request, user_submitted_id):
    if request.method == 'POST':
            timesheet_submitted = get_object_or_404(TimesheetSubmission, id=user_submitted_id)
            timesheet_submitted.delete()
            return JsonResponse({'success': True, 'message': 'Timesheet deleted successfully.'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

@login_required
def api_timesheets(request):
    user_id = request.GET.get('user_id')
    start_param = request.GET.get('start')
    end_param = request.GET.get('end')
    start_date = datetime.strptime(start_param, '%Y-%m-%d')
    end_date = datetime.strptime(end_param, '%Y-%m-%d')
    if start_param and end_param:
        timesheets = Timesheets.objects.filter(user=user_id, date__range=[start_date, end_date],status__in=["submitted","Approved"]).order_by('-date')
    else:
        timesheets = Timesheets.objects.filter(date__range=[start_date, end_date],status__in=["submitted","Approved"]).order_by('-date')
    timesheet_data = [{
        'title': timesheet.title,
        'date': timesheet.date.strftime('%Y-%m-%d'),
        'start_time': timesheet.start_time.strftime('%H:%M'),
        'end_time': timesheet.end_time.strftime('%H:%M'),
        'project_name': timesheet.project_name,
        'status':timesheet.status
    } for timesheet in timesheets]

    return JsonResponse(timesheet_data, safe=False)


@login_required
@csrf_exempt
def approve_timesheets(request):
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        month = int(request.POST.get('month'))
        year = int(request.POST.get('year'))
        Timesheets.objects.filter(user_id=user_id, date__year=year, date__month=month).update(status="Approved")
        return JsonResponse({'success': True, 'message': 'All timesheets have been approved.'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


@login_required
@csrf_exempt
def reject_timesheets(request):
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        month = int(request.POST.get('month'))
        year = int(request.POST.get('year'))

        Timesheets.objects.filter(user_id=user_id, date__year=year, date__month=month).delete()
        TimesheetSubmission.objects.filter(user_id=user_id, year=year, month=month).update(submitted=False)
        # TimesheetSubmission.objects.filter(user=request.user, year=year, month=month).delete()
                                           
        return JsonResponse({'success': True, 'message': 'All timesheets have been rejected.'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

