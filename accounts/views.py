from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import RegisterForm, LoginForm, UserProfileForm
from .models import UserProfile, AuditLog, Notification
from teams.models import Team
from organisation.models import Department
from messages_app.models import Message
from schedule.models import Meeting
from django.utils import timezone


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            AuditLog.objects.create(
                user=user, action='CREATE', model_name='User',
                object_id=user.id, description=f"New user registered: {user.username}"
            )
            login(request, user)
            messages.success(request, f"Welcome to Broadcast Portal, {user.first_name or user.username}!")
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            AuditLog.objects.create(
                user=user, action='LOGIN', model_name='User',
                object_id=user.id, description=f"User logged in: {user.username}"
            )
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.user.is_authenticated:
        AuditLog.objects.create(
            user=request.user, action='LOGOUT', model_name='User',
            object_id=request.user.id, description=f"User logged out: {request.user.username}"
        )
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


@login_required
def dashboard_view(request):
    team_count = Team.objects.filter(status='active').count()
    dept_count = Department.objects.count()
    unread_messages = Message.objects.filter(
    recipient=request.user,
    is_read=False,
    is_deleted_by_recipient=False,
    status='sent'
).count()
    upcoming_meetings = Meeting.objects.filter(
        attendees=request.user, status='scheduled', date_time__gte=timezone.now()
    ).order_by('date_time')[:3]
    recent_teams = Team.objects.filter(status='active').order_by('-created_at')[:5]
    recent_audit = AuditLog.objects.all()[:10]

    context = {
        'team_count': team_count,
        'dept_count': dept_count,
        'unread_messages': unread_messages,
        'upcoming_meetings': upcoming_meetings,
        'recent_teams': recent_teams,
        'recent_audit': recent_audit,
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.user, request.POST, instance=profile)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            profile = form.save(commit=False)
            profile.avatar_initials = ''
            profile.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        form = UserProfileForm(request.user, instance=profile)
    return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully!")
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)
        for field in form.fields:
            form.fields[field].widget.attrs.update({'class': 'form-control'})
    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
def mark_notification_read(request, pk):
    """Mark a single notification as read"""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    if notification.link:
        return redirect(notification.link)
    return redirect('dashboard')


@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('dashboard')


def forgot_password_view(request):
    """Step 1 - Find account by username or email"""
    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip()
        user = None
        try:
            user = User.objects.get(username=identifier)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=identifier)
            except User.DoesNotExist:
                user = None

        if user:
            request.session['reset_user_id'] = user.id
            messages.success(request, f"Account found for {user.username}. Please set your new password.")
            return redirect('direct_reset_password')
        else:
            messages.error(request, "No account found with that username or email address.")

    return render(request, 'registration/forgot_password.html')


def direct_reset_password_view(request):
    """Step 2 - Set new password directly"""
    user_id = request.session.get('reset_user_id')
    if not user_id:
        messages.error(request, "Invalid session. Please start again.")
        return redirect('forgot_password')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "User not found. Please start again.")
        return redirect('forgot_password')

    if request.method == 'POST':
        password1 = request.POST.get('new_password1', '')
        password2 = request.POST.get('new_password2', '')

        if len(password1) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
        elif password1 != password2:
            messages.error(request, "Passwords do not match.")
        elif password1.isdigit():
            messages.error(request, "Password cannot be entirely numeric.")
        else:
            user.set_password(password1)
            user.save()
            del request.session['reset_user_id']
            messages.success(request, "Password reset successfully! You can now log in.")
            return redirect('login')

    return render(request, 'registration/direct_reset_password.html', {'username': user.username})