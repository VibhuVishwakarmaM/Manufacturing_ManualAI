from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .models import Machine
from .serializers import MachineSerializer
from apps.accounts.permissions import IsAdministrator, user_is_administrator
from apps.audit_logs.utils import log_audit_event

# -----------------------------------------------------------------------------
# WEB TEMPLATE VIEWS
# -----------------------------------------------------------------------------

@login_required
def machine_list_view(request):
    machines = Machine.objects.all().prefetch_related('manuals')
    is_admin = user_is_administrator(request.user)
    return render(request, 'machines/machine_list.html', {
        'machines': machines,
        'is_admin': is_admin
    })

@login_required
def machine_create_view(request):
    if not user_is_administrator(request.user):
        messages.error(request, "Access denied: Only Administrators can register machines.")
        return redirect('machines:list')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        model_number = request.POST.get('model_number', '').strip()
        manufacturer = request.POST.get('manufacturer', '').strip()
        description = request.POST.get('description', '').strip()
        m_status = request.POST.get('status', 'ACTIVE')

        if not name or not model_number:
            messages.error(request, "Name and Model Number are required.")
            return render(request, 'machines/machine_form.html', {'title': 'Register New Machine'})

        machine = Machine.objects.create(
            name=name,
            model_number=model_number,
            manufacturer=manufacturer,
            description=description,
            status=m_status
        )
        log_audit_event(
            user=request.user,
            action='CREATE_MACHINE',
            resource_type='Machine',
            resource_id=str(machine.id),
            metadata={'name': name, 'model_number': model_number},
            request=request
        )
        messages.success(request, f"Machine '{name}' registered successfully.")
        return redirect('machines:list')

    return render(request, 'machines/machine_form.html', {'title': 'Register New Machine'})

@login_required
def machine_edit_view(request, pk):
    if not user_is_administrator(request.user):
        messages.error(request, "Access denied.")
        return redirect('machines:list')

    machine = get_object_or_404(Machine, pk=pk)

    if request.method == 'POST':
        machine.name = request.POST.get('name', '').strip()
        machine.model_number = request.POST.get('model_number', '').strip()
        machine.manufacturer = request.POST.get('manufacturer', '').strip()
        machine.description = request.POST.get('description', '').strip()
        machine.status = request.POST.get('status', 'ACTIVE')
        machine.save()

        log_audit_event(
            user=request.user,
            action='UPDATE_MACHINE',
            resource_type='Machine',
            resource_id=str(machine.id),
            metadata={'name': machine.name, 'model_number': machine.model_number},
            request=request
        )
        messages.success(request, f"Machine '{machine.name}' updated successfully.")
        return redirect('machines:list')

    return render(request, 'machines/machine_form.html', {
        'title': f'Edit Machine: {machine.name}',
        'machine': machine
    })

@login_required
@require_POST
def machine_delete_view(request, pk):
    if not user_is_administrator(request.user):
        messages.error(request, "Access denied.")
        return redirect('machines:list')

    machine = get_object_or_404(Machine, pk=pk)
    # Safeguard check
    if machine.manuals.exists() and not request.POST.get('confirm_force_delete'):
        messages.error(
            request, 
            f"Cannot delete machine '{machine.name}' because it has {machine.manuals.count()} manual(s) associated. "
            f"Please remove associated manuals first or confirm forced deletion."
        )
        return redirect('machines:list')

    m_name = machine.name
    m_id = str(machine.id)
    machine.delete()

    log_audit_event(
        user=request.user,
        action='DELETE_MACHINE',
        resource_type='Machine',
        resource_id=m_id,
        metadata={'name': m_name},
        request=request
    )
    messages.success(request, f"Machine '{m_name}' deleted successfully.")
    return redirect('machines:list')


# -----------------------------------------------------------------------------
# REST API VIEWS
# -----------------------------------------------------------------------------

class MachineListCreateAPIView(generics.ListCreateAPIView):
    queryset = Machine.objects.all().order_by('name')
    serializer_class = MachineSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsAdministrator()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        machine = serializer.save()
        log_audit_event(
            user=self.request.user,
            action='API_CREATE_MACHINE',
            resource_type='Machine',
            resource_id=str(machine.id),
            metadata={'name': machine.name, 'model_number': machine.model_number},
            request=self.request
        )

class MachineDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), IsAdministrator()]
        return [permissions.IsAuthenticated()]

    def perform_destroy(self, instance):
        # Safeguard: if manuals exist and query param ?force=true is not passed, reject
        force = self.request.query_params.get('force', 'false').lower() == 'true'
        if instance.manuals.exists() and not force:
            raise serializers.ValidationError(
                {"detail": f"Machine has {instance.manuals.count()} associated manual(s). Use ?force=true to override."}
            )
        m_id = str(instance.id)
        m_name = instance.name
        instance.delete()
        log_audit_event(
            user=self.request.user,
            action='API_DELETE_MACHINE',
            resource_type='Machine',
            resource_id=m_id,
            metadata={'name': m_name},
            request=self.request
        )
