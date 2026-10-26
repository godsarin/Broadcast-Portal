from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
import json
from datetime import timedelta
from .models import Meeting
from .forms import MeetingForm


@login_required
def schedule_home(request):
    """Main schedule page with monthly view - Student 4"""
    now = timezone.now()

    upcoming = Meeting.objects.filter(
        Q(organiser=request.user) | Q(attendees=request.user),
        date_time__gte=now,
        status='scheduled'
    ).distinct().order_by('date_time')[:10]

    this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    next_month = (this_month_start + timedelta(days=32)).replace(day=1)

    monthly = Meeting.objects.filter(
        Q(organiser=request.user) | Q(attendees=request.user),
        date_time__range=(this_month_start, next_month),
        status='scheduled'
    ).distinct().order_by('date_time')

    # Build calendar data for JS
    calendar_events = []
    for m in monthly:
        calendar_events.append({
            'id': m.id,
            'title': m.title,
            'start': m.date_time.isoformat(),
            'end': (m.date_time + timedelta(minutes=m.duration_minutes)).isoformat(),
            'color': '#8E32E9' if m.organiser == request.user else '#198754',
        })

    context = {
        'upcoming': upcoming,
        'weekly': monthly,
        'monthly': monthly,
        'calendar_events_json': json.dumps(calendar_events),
        'now': now,
    }
    return render(request, 'schedule/schedule_home.html', context)


@login_required
def meeting_create(request):
    """Schedule a new meeting - Student 4"""
    initial = {}
    team_id = request.GET.get('team')
    if team_id:
        from teams.models import Team
        try:
            team = Team.objects.get(pk=team_id)
            initial['team'] = team
            initial['title'] = f"Meeting - {team.name}"
        except Team.DoesNotExist:
            pass

    if request.method == 'POST':
        form = MeetingForm(request.POST, is_edit=False)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.organiser = request.user
            meeting.save()
            form.save_m2m()
            meeting.attendees.add(request.user)

            from accounts.models import Notification
            for attendee in meeting.attendees.all():
                if attendee != request.user:
                    Notification.objects.create(
                        user=attendee,
                        notification_type='meeting',
                        title=f'Meeting invite: {meeting.title}',
                        message=f'Scheduled for {meeting.date_time.strftime("%d %b %Y %H:%M")}',
                        link=f'/schedule/meetings/{meeting.pk}/'
                    )

            messages.success(request, f"Meeting '{meeting.title}' scheduled!")
            return redirect('meeting_detail', pk=meeting.pk)
    else:
        form = MeetingForm(initial=initial, is_edit=False)
    return render(request, 'schedule/meeting_form.html', {
        'form': form, 'title': 'Schedule Meeting'
    })


@login_required
def meeting_detail(request, pk):
    """Meeting detail - Student 4"""
    meeting = get_object_or_404(Meeting, pk=pk)
    is_organiser = meeting.organiser == request.user
    is_attendee = request.user in meeting.attendees.all()
    return render(request, 'schedule/meeting_detail.html', {
        'meeting': meeting,
        'is_organiser': is_organiser,
        'is_attendee': is_attendee,
    })


@login_required
def meeting_edit(request, pk):
    """Edit meeting - Student 4"""
    meeting = get_object_or_404(Meeting, pk=pk)
    if meeting.organiser != request.user and not request.user.is_staff:
        messages.error(request, "Only the organiser can edit this meeting.")
        return redirect('meeting_detail', pk=pk)
    if request.method == 'POST':
        form = MeetingForm(request.POST, instance=meeting, is_edit=True)
        if form.is_valid():
            form.save()
            messages.success(request, "Meeting updated!")
            return redirect('meeting_detail', pk=pk)
    else:
        form = MeetingForm(instance=meeting, is_edit=True)
    return render(request, 'schedule/meeting_form.html', {
        'form': form, 'title': 'Edit Meeting', 'meeting': meeting
    })


@login_required
def meeting_cancel(request, pk):
    """Cancel a meeting - Student 4"""
    meeting = get_object_or_404(Meeting, pk=pk)
    if meeting.organiser != request.user and not request.user.is_staff:
        messages.error(request, "Only the organiser can cancel this meeting.")
        return redirect('meeting_detail', pk=pk)
    if request.method == 'POST':
        meeting.status = 'cancelled'
        meeting.save()
        messages.success(request, "Meeting cancelled.")
        return redirect('schedule_home')
    return render(request, 'schedule/meeting_cancel.html', {'meeting': meeting})


@login_required
def my_meetings(request):
    """All my meetings - Student 4"""
    status_filter = request.GET.get('status', '')
    meetings_qs = Meeting.objects.filter(
        Q(organiser=request.user) | Q(attendees=request.user)
    ).distinct().order_by('-date_time')
    if status_filter:
        meetings_qs = meetings_qs.filter(status=status_filter)
    return render(request, 'schedule/my_meetings.html', {
        'meetings': meetings_qs,
        'status_filter': status_filter,
    })


@login_required
def meeting_delete(request, pk):
    """Permanently delete any meeting - Student 4"""
    meeting = get_object_or_404(Meeting, pk=pk)
    if meeting.organiser != request.user and not request.user.is_staff:
        messages.error(request, "Only the organiser can delete this meeting.")
        return redirect('my_meetings')
    if request.method == 'POST':
        meeting.delete()
        messages.success(request, "Meeting deleted successfully.")
        return redirect('my_meetings')
    return redirect('my_meetings')