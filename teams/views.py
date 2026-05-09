from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Team, TeamMembership, CodeRepository, Skill
from .forms import TeamForm, TeamMembershipForm, CodeRepositoryForm
from accounts.models import AuditLog


# ─────────────────────────────────────────────
#  TEAM LIST — Browse & Search
# ─────────────────────────────────────────────

@login_required
def team_list(request):
    """
    Display all teams with search and filter functionality.

    Supports:
    - Text search across name, description, department, and manager name (Q objects)
    - Filter by status (active / restructured / disbanded)
    - Filter by department

    Author: Sarin Pradhan (Student 1)
    """
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', 'active')
    dept_filter = request.GET.get('department', '')

    # select_related: SQL JOIN for ForeignKey fields (avoids N+1 queries)
    # prefetch_related: separate query for ManyToMany/reverse FK (memberships)
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


# ─────────────────────────────────────────────
#  TEAM DETAIL — Full Profile View
# ─────────────────────────────────────────────

@login_required
def team_detail(request, pk):
    """
    Show full profile of a single team including:
    - Members table (with add/remove for managers/staff)
    - Code repositories
    - Upstream and downstream dependencies
    - Skills
    - Contact info (Slack, email, manager)

    can_edit is True for staff users OR the team's own manager.

    Author: Sarin Pradhan (Student 1)
    """
    team = get_object_or_404(Team, pk=pk)
    members = team.get_members()
    repos = team.repositories.filter(is_active=True)
    upstream = team.upstream_dependencies.all()
    downstream = team.downstream_dependents.all()      # auto reverse ManyToMany
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


# ─────────────────────────────────────────────
#  TEAM CREATE
# ─────────────────────────────────────────────

@login_required
def team_create(request):
    """
    Allow staff/admin to create a new team.
    Logs the action to the shared AuditLog model.

    Author: Sarin Pradhan (Student 1)
    """
    if not request.user.is_staff:
        messages.error(request, "Only administrators can create teams.")
        return redirect('team_list')

    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            team = form.save()
            AuditLog.objects.create(
                user=request.user,
                action='CREATE',
                model_name='Team',
                object_id=team.id,
                description=f"Team created: {team.name}"
            )
            messages.success(request, f"Team '{team.name}' created successfully!")
            return redirect('team_detail', pk=team.pk)
    else:
        form = TeamForm()

    return render(request, 'teams/team_form.html', {'form': form, 'title': 'Create Team'})


# ─────────────────────────────────────────────
#  TEAM EDIT
# ─────────────────────────────────────────────

@login_required
def team_edit(request, pk):
    """
    Allow staff OR the team's own manager to edit team details.
    Logs the action to the shared AuditLog model.

    Author: Sarin Pradhan (Student 1)
    """
    team = get_object_or_404(Team, pk=pk)

    if not (request.user.is_staff or team.manager == request.user):
        messages.error(request, "You don't have permission to edit this team.")
        return redirect('team_detail', pk=pk)

    if request.method == 'POST':
        form = TeamForm(request.POST, instance=team)
        if form.is_valid():
            form.save()
            AuditLog.objects.create(
                user=request.user,
                action='UPDATE',
                model_name='Team',
                object_id=team.id,
                description=f"Team updated: {team.name}"
            )
            messages.success(request, "Team updated successfully!")
            return redirect('team_detail', pk=pk)
    else:
        form = TeamForm(instance=team)

    return render(request, 'teams/team_form.html', {
        'form': form,
        'title': 'Edit Team',
        'team': team
    })


# ─────────────────────────────────────────────
#  TEAM DELETE (soft-delete — sets status to 'disbanded')
# ─────────────────────────────────────────────

@login_required
def team_delete(request, pk):
    """
    Soft-delete a team by setting status='disbanded'.
    The team record and its history are preserved — never hard-deleted.
    Only staff/admin can disband a team.
    Logs the action to the shared AuditLog model.

    Author: Sarin Pradhan (Student 1)
    """
    team = get_object_or_404(Team, pk=pk)

    if not request.user.is_staff:
        messages.error(request, "Only administrators can delete teams.")
        return redirect('team_detail', pk=pk)

    if request.method == 'POST':
        name = team.name
        team.status = 'disbanded'
        team.save()
        AuditLog.objects.create(
            user=request.user,
            action='DELETE',
            model_name='Team',
            object_id=team.id,
            description=f"Team disbanded: {name}"
        )
        messages.success(request, f"Team '{name}' has been disbanded.")
        return redirect('team_list')

    return render(request, 'teams/team_confirm_delete.html', {'team': team})


# ─────────────────────────────────────────────
#  ADD MEMBER
# ─────────────────────────────────────────────

@login_required
def team_add_member(request, pk):
    """
    Add a user to a team with a specified role.

    Smart re-activation: if the user was previously a member (is_active=False),
    re-adding them re-activates the existing record instead of creating a duplicate
    (which would violate the unique_together constraint).

    On success, sends a Notification to the added user.
    Logs the action to the shared AuditLog model.

    Author: Sarin Pradhan (Student 1)
    """
    team = get_object_or_404(Team, pk=pk)

    if not (request.user.is_staff or team.manager == request.user):
        messages.error(request, "Permission denied.")
        return redirect('team_detail', pk=pk)

    if request.method == 'POST':
        form = TeamMembershipForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']

            # Check if already a member (active or previously removed)
            existing = TeamMembership.objects.filter(team=team, user=user).first()
            if existing:
                if existing.is_active:
                    messages.error(
                        request,
                        f"{user.get_full_name() or user.username} is already a member of this team."
                    )
                    return render(request, 'teams/add_member.html', {'form': form, 'team': team})
                else:
                    # Re-activate previously removed member
                    existing.is_active = True
                    existing.role = form.cleaned_data['role']
                    existing.save()
                    messages.success(
                        request,
                        f"{user.get_full_name() or user.username} re-added to team!"
                    )
                    return redirect('team_detail', pk=pk)

            membership = form.save(commit=False)
            membership.team = team
            membership.save()

            AuditLog.objects.create(
                user=request.user,
                action='UPDATE',
                model_name='Team',
                object_id=team.id,
                description=f"Member added to {team.name}: {user.username}"
            )

            # Notify the added user (integrates with shared accounts app)
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


# ─────────────────────────────────────────────
#  REMOVE MEMBER (soft-delete — sets is_active=False)
# ─────────────────────────────────────────────

@login_required
def team_remove_member(request, pk, membership_id):
    """
    Soft-remove a member by setting is_active=False.
    Record is preserved for audit history.

    Author: Sarin Pradhan (Student 1)
    """
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

    return render(request, 'teams/confirm_remove_member.html', {
        'membership': membership,
        'team': team
    })


# ─────────────────────────────────────────────
#  ADD CODE REPOSITORY
# ─────────────────────────────────────────────

@login_required
def team_add_repo(request, pk):
    """
    Add a code repository (GitHub, GitLab, etc.) to a team.
    Only accessible by staff or the team manager.

    Author: Sarin Pradhan (Student 1)
    """
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


# ─────────────────────────────────────────────
#  EMAIL TEAM — Integration with messages_app (Student 3)
# ─────────────────────────────────────────────

@login_required
def email_team(request, pk):
    """
    Contact a team by sending an internal message to the team manager.

    Integration point with Student 3 (Chris):
    Creates a Message object in messages_app.models.Message
    and a Notification for the manager via accounts.models.Notification.

    Author: Sarin Pradhan (Student 1)
    """
    team = get_object_or_404(Team, pk=pk)

    if request.method == 'POST':
        subject = request.POST.get('subject', '')
        message_body = request.POST.get('message', '')

        if subject and message_body:
            # Integrate with Chris's (Student 3) messages_app
            from messages_app.models import Message
            if team.manager:
                Message.objects.create(
                    sender=request.user,
                    recipient=team.manager,
                    subject=f"[Team: {team.name}] {subject}",
                    body=message_body,
                    status='sent'
                )
                # Notify the manager via shared accounts Notification model
                from accounts.models import Notification
                Notification.objects.create(
                    user=team.manager,
                    notification_type='message',
                    title=f'New message about {team.name}',
                    message=subject,
                    link='/messages/'
                )
                messages.success(
                    request,
                    f"Message sent to {team.manager.get_full_name() or team.manager.username}!"
                )
            else:
                messages.warning(
                    request,
                    "This team has no manager assigned. Message could not be sent."
                )
            return redirect('team_detail', pk=pk)

    return render(request, 'teams/email_team.html', {'team': team})
