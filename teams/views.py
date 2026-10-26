from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import Team, TeamMembership, CodeRepository, Skill
from .forms import TeamForm, TeamMembershipForm, CodeRepositoryForm
from accounts.models import AuditLog


@login_required
def team_list(request):
    """Display all teams with search functionality - Student 1"""
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', 'active')
    dept_filter = request.GET.get('department', '')

    teams = Team.objects.select_related('department', 'manager').prefetch_related('memberships')

    if query:
        teams = teams.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(department__name__icontains=query) |
            Q(manager__first_name__icontains=query) |
            Q(manager__last_name__icontains=query)
        )
    if status_filter:
        teams = teams.filter(status=status_filter)
    if dept_filter:
        teams = teams.filter(department__id=dept_filter)

    from organisation.models import Department
    departments = Department.objects.all()

    context = {
        'teams': teams,
        'query': query,
        'status_filter': status_filter,
        'dept_filter': dept_filter,
        'departments': departments,
    }
    return render(request, 'teams/team_list.html', context)


@login_required
def team_detail(request, pk):
    """Detailed team view with all info - Student 1"""
    team = get_object_or_404(Team, pk=pk)
    members = team.get_members()
    repos = team.repositories.filter(is_active=True)
    upstream = team.upstream_dependencies.all()
    downstream = team.downstream_dependents.all()
    can_edit = request.user.is_staff or (team.manager == request.user)

    context = {
        'team': team,
        'members': members,
        'repos': repos,
        'upstream': upstream,
        'downstream': downstream,
        'can_edit': can_edit,
    }
    return render(request, 'teams/team_detail.html', context)


@login_required
def team_create(request):
    if not request.user.is_staff:
        messages.error(request, "Only administrators can create teams.")
        return redirect('team_list')
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            team = form.save()
            AuditLog.objects.create(
                user=request.user, action='CREATE', model_name='Team',
                object_id=team.id, description=f"Team created: {team.name}"
            )
            messages.success(request, f"Team '{team.name}' created successfully!")
            return redirect('team_detail', pk=team.pk)
    else:
        form = TeamForm()
    return render(request, 'teams/team_form.html', {'form': form, 'title': 'Create Team'})


@login_required
def team_edit(request, pk):
    team = get_object_or_404(Team, pk=pk)
    if not (request.user.is_staff or team.manager == request.user):
        messages.error(request, "You don't have permission to edit this team.")
        return redirect('team_detail', pk=pk)
    if request.method == 'POST':
        form = TeamForm(request.POST, instance=team)
        if form.is_valid():
            form.save()
            AuditLog.objects.create(
                user=request.user, action='UPDATE', model_name='Team',
                object_id=team.id, description=f"Team updated: {team.name}"
            )
            messages.success(request, "Team updated successfully!")
            return redirect('team_detail', pk=pk)
    else:
        form = TeamForm(instance=team)
    return render(request, 'teams/team_form.html', {'form': form, 'title': 'Edit Team', 'team': team})


@login_required
def team_delete(request, pk):
    team = get_object_or_404(Team, pk=pk)
    if not request.user.is_staff:
        messages.error(request, "Only administrators can delete teams.")
        return redirect('team_detail', pk=pk)
    if request.method == 'POST':
        name = team.name
        team.status = 'disbanded'
        team.save()
        AuditLog.objects.create(
            user=request.user, action='DELETE', model_name='Team',
            object_id=team.id, description=f"Team disbanded: {name}"
        )
        messages.success(request, f"Team '{name}' has been disbanded.")
        return redirect('team_list')
    return render(request, 'teams/team_confirm_delete.html', {'team': team})


@login_required
def team_add_member(request, pk):
    team = get_object_or_404(Team, pk=pk)
    if not (request.user.is_staff or team.manager == request.user):
        messages.error(request, "Permission denied.")
        return redirect('team_detail', pk=pk)
    if request.method == 'POST':
        form = TeamMembershipForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            # Check if already a member
            existing = TeamMembership.objects.filter(team=team, user=user).first()
            if existing:
                if existing.is_active:
                    messages.error(request, f"{user.get_full_name() or user.username} is already a member of this team.")
                    return render(request, 'teams/add_member.html', {'form': form, 'team': team})
                else:
                    # Re-activate if previously removed
                    existing.is_active = True
                    existing.role = form.cleaned_data['role']
                    existing.save()
                    messages.success(request, f"{user.get_full_name() or user.username} re-added to team!")
                    return redirect('team_detail', pk=pk)
            membership = form.save(commit=False)
            membership.team = team
            membership.save()
            AuditLog.objects.create(
                user=request.user, action='UPDATE', model_name='Team',
                object_id=team.id,
                description=f"Member added to {team.name}: {user.username}"
            )
            # Notify the user they were added
            from accounts.models import Notification
            Notification.objects.create(
                user=membership.user,
                notification_type='team',
                title=f'You were added to {team.name}',
                message=f'You have been added as {membership.get_role_display()}',
                link=f'/teams/{team.pk}/'
            )
            messages.success(request, "Member added successfully!")
            return redirect('team_detail', pk=pk)
    else:
        form = TeamMembershipForm()
    return render(request, 'teams/add_member.html', {'form': form, 'team': team})


@login_required
def team_remove_member(request, pk, membership_id):
    team = get_object_or_404(Team, pk=pk)
    membership = get_object_or_404(TeamMembership, pk=membership_id, team=team)
    if not (request.user.is_staff or team.manager == request.user):
        messages.error(request, "Permission denied.")
        return redirect('team_detail', pk=pk)
    if request.method == 'POST':
        membership.is_active = False
        membership.save()
        messages.success(request, f"{membership.user.username} removed from team.")
        return redirect('team_detail', pk=pk)
    return render(request, 'teams/confirm_remove_member.html', {'membership': membership, 'team': team})


@login_required
def team_add_repo(request, pk):
    team = get_object_or_404(Team, pk=pk)
    if not (request.user.is_staff or team.manager == request.user):
        messages.error(request, "Permission denied.")
        return redirect('team_detail', pk=pk)
    if request.method == 'POST':
        form = CodeRepositoryForm(request.POST)
        if form.is_valid():
            repo = form.save(commit=False)
            repo.team = team
            repo.save()
            messages.success(request, "Repository added!")
            return redirect('team_detail', pk=pk)
    else:
        form = CodeRepositoryForm()
    return render(request, 'teams/add_repo.html', {'form': form, 'team': team})


@login_required
def email_team(request, pk):
    """Email team contact form - Student 1"""
    team = get_object_or_404(Team, pk=pk)
    if request.method == 'POST':
        subject = request.POST.get('subject', '')
        message_body = request.POST.get('message', '')
        if subject and message_body:
            from messages_app.models import Message
            if team.manager:
                Message.objects.create(
                    sender=request.user,
                    recipient=team.manager,
                    subject=f"[Team: {team.name}] {subject}",
                    body=message_body,
                    status='sent'
                )
                # Notify the manager
                from accounts.models import Notification
                Notification.objects.create(
                    user=team.manager,
                    notification_type='message',
                    title=f'New message about {team.name}',
                    message=subject,
                    link=f'/messages/'
                )
                messages.success(request, f"Message sent to {team.manager.get_full_name() or team.manager.username}!")
            else:
                messages.warning(request, "This team has no manager assigned. Message could not be sent.")
            return redirect('team_detail', pk=pk)
    return render(request, 'teams/email_team.html', {'team': team})