from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Department, TeamType, OrganisationStructure
from .forms import DepartmentForm, TeamTypeForm
from accounts.models import AuditLog


@login_required
def organisation_overview(request):
    """Organisation overview with org chart data - Student 2"""
    departments = Department.objects.prefetch_related(
        'teams', 'teams__memberships', 'leader'
    ).all()

    # Build org chart data for D3/JS
    org_data = []
    for dept in departments:
        active_teams = dept.teams.filter(status='active')
        dept_node = {
            'id': f'dept_{dept.id}',
            'name': dept.name,
            'type': 'department',
            'leader': dept.leader.get_full_name() if dept.leader else 'N/A',
            'team_count': active_teams.count(),
        }
        org_data.append(dept_node)

    context = {
        'departments': departments,
        'org_data': org_data,
    }
    return render(request, 'organisation/overview.html', context)


@login_required
def dependency_map(request):
    """Visualise upstream/downstream dependencies - Student 2"""
    from teams.models import Team
    teams = Team.objects.filter(status='active').prefetch_related(
        'upstream_dependencies', 'downstream_dependents', 'department'
    )

    # Build dependency graph data — only active teams
    active_ids = set(teams.values_list('id', flat=True))
    nodes = []
    edges = []
    for team in teams:
        nodes.append({
            'id': team.id,
            'label': team.name,
            'dept': team.department.name if team.department else 'Unassigned',
        })
        for upstream in team.upstream_dependencies.all():
            # Only include edge if upstream team is also active
            if upstream.id in active_ids:
                edges.append({'from': upstream.id, 'to': team.id})

    context = {
        'teams': teams,
        'nodes': nodes,
        'edges': edges,
    }
    return render(request, 'organisation/dependency_map.html', context)

    # Build dependency graph data
    nodes = []
    edges = []
    for team in teams:
        nodes.append({
            'id': team.id,
            'label': team.name,
            'dept': team.department.name if team.department else 'Unassigned',
        })
        for upstream in team.upstream_dependencies.all():
            edges.append({'from': upstream.id, 'to': team.id})

    context = {
        'teams': teams,
        'nodes': nodes,
        'edges': edges,
    }
    return render(request, 'organisation/dependency_map.html', context)


@login_required
def department_list(request):
    """List all departments - Student 2"""
    query = request.GET.get('q', '')
    departments = Department.objects.prefetch_related('teams').all()
    if query:
        departments = departments.filter(
            Q(name__icontains=query) |
            Q(specialisation__icontains=query) |
            Q(leader__first_name__icontains=query) |
            Q(leader__last_name__icontains=query)
        )
    return render(request, 'organisation/department_list.html', {
        'departments': departments, 'query': query
    })


@login_required
def department_detail(request, pk):
    """Department detail page - Student 2"""
    dept = get_object_or_404(Department, pk=pk)
    active_teams = dept.teams.filter(status='active').prefetch_related('memberships')
    all_members = set()
    for team in active_teams:
        for m in team.get_members():
            all_members.add(m.user)

    context = {
        'dept': dept,
        'active_teams': active_teams,
        'all_members': all_members,
    }
    return render(request, 'organisation/department_detail.html', context)


@login_required
def department_create(request):
    if not request.user.is_staff:
        messages.error(request, "Permission denied.")
        return redirect('department_list')
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            dept = form.save()
            AuditLog.objects.create(
                user=request.user, action='CREATE', model_name='Department',
                object_id=dept.id, description=f"Department created: {dept.name}"
            )
            messages.success(request, f"Department '{dept.name}' created!")
            return redirect('department_detail', pk=dept.pk)
    else:
        form = DepartmentForm()
    return render(request, 'organisation/department_form.html', {
        'form': form, 'title': 'Create Department'
    })


@login_required
def department_edit(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if not request.user.is_staff:
        messages.error(request, "Permission denied.")
        return redirect('department_detail', pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=dept)
        if form.is_valid():
            form.save()
            AuditLog.objects.create(
                user=request.user, action='UPDATE', model_name='Department',
                object_id=dept.id, description=f"Department updated: {dept.name}"
            )
            messages.success(request, "Department updated!")
            return redirect('department_detail', pk=pk)
    else:
        form = DepartmentForm(instance=dept)
    return render(request, 'organisation/department_form.html', {
        'form': form, 'title': 'Edit Department', 'dept': dept
    })


@login_required
def teamtype_list(request):
    """Team types management - Student 2"""
    types = TeamType.objects.all()
    return render(request, 'organisation/teamtype_list.html', {'types': types})


@login_required
def teamtype_create(request):
    if not request.user.is_staff:
        messages.error(request, "Permission denied.")
        return redirect('teamtype_list')
    if request.method == 'POST':
        form = TeamTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Team type created!")
            return redirect('teamtype_list')
    else:
        form = TeamTypeForm()
    return render(request, 'organisation/teamtype_form.html', {'form': form})

@login_required
def department_delete(request, pk):
    """Delete a department"""
    if not request.user.is_staff:
        messages.error(request, "Only administrators can delete departments.")
        return redirect('department_list')
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        name = dept.name
        dept.delete()
        AuditLog.objects.create(
            user=request.user, action='DELETE', model_name='Department',
            object_id=pk, description=f"Department deleted: {name}"
        )
        messages.success(request, f"Department '{name}' deleted successfully.")
        return redirect('department_list')
    return redirect('department_detail', pk=pk)