from django.shortcuts import render, redirect, get_object_or_404
from .models import Member, Activity, ActivityLog
from .forms import MemberForm, ActivityLogForm, BulkMemberForm
from django.http import HttpResponse
import pandas as pd
from io import BytesIO

def member_list(request):
    members = Member.objects.all().order_by('name')
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('member_list')
    else:
        form = MemberForm()
    return render(request, 'member_list.html', {'members': members, 'form': form})

def delete_member(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    member.delete()
    return redirect('member_list')

def bulk_member_add(request):
    if request.method == 'POST':
        form = BulkMemberForm(request.POST)
        if form.is_valid():
            names = form.cleaned_data['names']
            name_list = [name.strip() for name in names.replace(',', '\n').split('\n') if name.strip()]
            for name in name_list:
                Member.objects.get_or_create(name=name)
            return redirect('member_list')
    else:
        form = BulkMemberForm()
    return render(request, 'bulk_member_add.html', {'form': form})

def activity_log(request):
    if request.method == 'POST':
        form = ActivityLogForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            activity_name = form.cleaned_data['activity_name']
            participants = form.cleaned_data['participants']
            duration = form.cleaned_data['duration']

            # 활동 생성
            activity, created = Activity.objects.get_or_create(date=date, activity_name=activity_name)
            
            # 시간 처리
            duration_minutes = 0
            if '시간' in duration:
                hours, minutes = duration.split('시간')
                duration_minutes += int(hours.strip()) * 60
                if '분' in minutes:
                    minutes = minutes.split('분')[0].strip()
                    duration_minutes += int(minutes)
            elif '분' in duration:
                duration_minutes += int(duration.split('분')[0].strip())

            # 활동 로그 생성
            for participant in participants:
                ActivityLog.objects.create(activity=activity, participant=participant, duration=duration_minutes)
                
            return redirect('activity_log')
    else:
        form = ActivityLogForm()
    
    if 'delete_activity' in request.GET:
        activity_id = request.GET.get('delete_activity')
        activity = get_object_or_404(Activity, id=activity_id)
        activity.delete()
        return redirect('activity_log')

    logs = ActivityLog.objects.all()
    members = Member.objects.all().order_by('name')
    
    # 참가자별 활동 여부와 총 활동 시간 계산
    activity_columns = logs.values_list('activity__activity_name', 'activity__date', 'activity__id').distinct()
    summary_data = {}
    for member in members:
        summary_data[member.name] = {
            'activities': {f"{activity_name}({date})": 'X' for activity_name, date, _ in activity_columns},
            'total_duration': 0
        }
        member_logs = logs.filter(participant=member)
        for log in member_logs:
            activity_key = f"{log.activity.activity_name}({log.activity.date})"
            summary_data[member.name]['activities'][activity_key] = 'O'
            summary_data[member.name]['total_duration'] += log.duration
    
    # 총 활동 시간을 시간과 분으로 변환
    for member in summary_data:
        total_minutes = summary_data[member]['total_duration']
        hours = total_minutes // 60
        minutes = total_minutes % 60
        summary_data[member]['total_duration'] = f"{hours}시간 {minutes}분"

    return render(request, 'activity_log.html', {
        'form': form,
        'logs': logs,
        'members': members,
        'summary_data': summary_data,
        'activity_columns': [(f"{activity_name}({date})", activity_id) for activity_name, date, activity_id in activity_columns]
    })

def download(request):
    logs = ActivityLog.objects.all()
    members = Member.objects.all().order_by('name')
    
    activity_columns = logs.values_list('activity__activity_name', 'activity__date').distinct()
    summary_data = []
    
    for member in members:
        row = {
            '이름': member.name,
            '총 활동시간': 0
        }
        for activity_name, date in activity_columns:
            row[f"{activity_name}({date})"] = 'X'
        
        member_logs = logs.filter(participant=member)
        for log in member_logs:
            activity_key = f"{log.activity.activity_name}({log.activity.date})"
            row[activity_key] = 'O'
            row['총 활동시간'] += log.duration
        
        total_minutes = row['총 활동시간']
        hours = total_minutes // 60
        minutes = total_minutes % 60
        row['총 활동시간'] = f"{hours}시간 {minutes}분"
        
        summary_data.append(row)
    
    df = pd.DataFrame(summary_data)

    # 컬럼 순서 조정
    columns = ['이름'] + [f"{activity_name}({date})" for activity_name, date in activity_columns] + ['총 활동시간']
    df = df[columns]

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='ActivityLog')
    output.seek(0)

    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=activity_log.xlsx'
    return response
