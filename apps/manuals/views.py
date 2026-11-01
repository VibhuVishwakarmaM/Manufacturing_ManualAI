import os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Manual
from .serializers import ManualSerializer, ManualUploadSerializer
from .validators import validate_pdf_file
from apps.machines.models import Machine
from apps.accounts.permissions import IsAdministrator, user_is_administrator
from apps.audit_logs.utils import log_audit_event
from apps.document_processing.processor import process_manual

# -----------------------------------------------------------------------------
# WEB TEMPLATE VIEWS
# -----------------------------------------------------------------------------

@login_required
def manual_list_view(request):
    machine_id = request.GET.get('machine')
    manuals_qs = Manual.objects.select_related('machine', 'uploaded_by').all()
    if machine_id:
        manuals_qs = manuals_qs.filter(machine_id=machine_id)

    machines = Machine.objects.all()
    is_admin = user_is_administrator(request.user)

    return render(request, 'manuals/manual_list.html', {
        'manuals': manuals_qs,
        'machines': machines,
        'selected_machine_id': machine_id,
        'is_admin': is_admin
    })

@login_required
def manual_upload_view(request):
    if not user_is_administrator(request.user):
        messages.error(request, "Access denied: Only Administrators can upload manuals.")
        return redirect('manuals:list')

    machines = Machine.objects.filter(status='ACTIVE')

    if request.method == 'POST':
        machine_id = request.POST.get('machine')
        title = request.POST.get('title', '').strip()
        revision = request.POST.get('revision', 'Rev 1.0').strip()
        model_info = request.POST.get('model_information', '').strip()
        pdf_file = request.FILES.get('file')

        if not machine_id or not title or not pdf_file:
            messages.error(request, "Please provide Machine, Manual Title, and select a PDF file.")
            return render(request, 'manuals/manual_upload.html', {'machines': machines})

        # Validate file
        try:
            validate_pdf_file(pdf_file)
        except Exception as ve:
            messages.error(request, f"Validation error: {ve}")
            return render(request, 'manuals/manual_upload.html', {'machines': machines})

        machine = get_object_or_404(Machine, pk=machine_id)

        manual = Manual.objects.create(
            machine=machine,
            title=title,
            file=pdf_file,
            original_filename=pdf_file.name,
            model_information=model_info,
            revision=revision,
            file_size=pdf_file.size,
            uploaded_by=request.user,
            processing_status=Manual.STATUS_UPLOADED
        )

        log_audit_event(
            user=request.user,
            action='UPLOAD_MANUAL',
            resource_type='Manual',
            resource_id=str(manual.id),
            metadata={'title': title, 'filename': pdf_file.name, 'machine': machine.name},
            request=request
        )

        messages.info(request, f"Manual '{title}' uploaded. Triggering extraction and embedding pipeline...")

        # Process document immediately
        result = process_manual(manual.id)
        if result.get('status') == 'SUCCESS':
            messages.success(request, f"Manual successfully processed: {result['page_count']} pages, {result['chunk_count']} chunks indexed.")
        else:
            messages.warning(request, f"Manual uploaded but indexing encountered an issue: {result.get('error')}. You can inspect errors and retry.")

        return redirect('manuals:list')

    return render(request, 'manuals/manual_upload.html', {'machines': machines})

@login_required
@require_POST
def manual_reprocess_view(request, pk):
    if not user_is_administrator(request.user):
        messages.error(request, "Access denied.")
        return redirect('manuals:list')

    manual = get_object_or_404(Manual, pk=pk)
    result = process_manual(manual.id, force_reprocess=True)

    if result.get('status') == 'SUCCESS':
        messages.success(request, f"Manual '{manual.title}' re-indexed successfully ({result['chunk_count']} chunks).")
    else:
        messages.error(request, f"Reprocessing failed: {result.get('error')}")

    return redirect('manuals:list')

@login_required
@require_POST
def manual_delete_view(request, pk):
    if not user_is_administrator(request.user):
        messages.error(request, "Access denied.")
        return redirect('manuals:list')

    manual = get_object_or_404(Manual, pk=pk)
    m_id = str(manual.id)
    title = manual.title

    # Delete physical file
    if manual.file:
        try:
            if os.path.isfile(manual.file.path):
                os.remove(manual.file.path)
        except Exception:
            pass

    manual.delete()
    log_audit_event(
        user=request.user,
        action='DELETE_MANUAL',
        resource_type='Manual',
        resource_id=m_id,
        metadata={'title': title},
        request=request
    )
    messages.success(request, f"Manual '{title}' and its indexed chunks were deleted.")
    return redirect('manuals:list')

@login_required
def manual_view_pdf_view(request, pk):
    """Secure authorized viewing of original equipment manual PDF."""
    manual = get_object_or_404(Manual, pk=pk)
    if not manual.file or not os.path.exists(manual.file.path):
        raise Http404("PDF document file was not found on server storage.")

    response = FileResponse(open(manual.file.path, 'rb'), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{manual.original_filename}"'
    return response

@login_required
def manual_download_pdf_view(request, pk):
    """Secure authorized download of equipment manual PDF."""
    manual = get_object_or_404(Manual, pk=pk)
    if not manual.file or not os.path.exists(manual.file.path):
        raise Http404("PDF document file was not found.")

    response = FileResponse(open(manual.file.path, 'rb'), as_attachment=True, filename=manual.original_filename)
    return response


# -----------------------------------------------------------------------------
# REST API VIEWS
# -----------------------------------------------------------------------------

class ManualListCreateAPIView(views.APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsAdministrator()]
        return [permissions.IsAuthenticated()]

    def get(self, request):
        machine_id = request.query_params.get('machine')
        qs = Manual.objects.select_related('machine', 'uploaded_by').all()
        if machine_id:
            qs = qs.filter(machine_id=machine_id)
        serializer = ManualSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ManualUploadSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        manual = serializer.save()

        log_audit_event(
            user=request.user,
            action='API_UPLOAD_MANUAL',
            resource_type='Manual',
            resource_id=str(manual.id),
            metadata={'title': manual.title, 'machine_id': str(manual.machine_id)},
            request=request
        )

        # Trigger processing
        process_manual(manual.id)
        manual.refresh_from_db()

        return Response(ManualSerializer(manual).data, status=status.HTTP_201_CREATED)

class ManualDetailAPIView(generics.RetrieveDestroyAPIView):
    queryset = Manual.objects.all()
    serializer_class = ManualSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [permissions.IsAuthenticated(), IsAdministrator()]
        return [permissions.IsAuthenticated()]

    def perform_destroy(self, instance):
        m_id = str(instance.id)
        title = instance.title
        instance.delete()
        log_audit_event(
            user=self.request.user,
            action='API_DELETE_MANUAL',
            resource_type='Manual',
            resource_id=m_id,
            metadata={'title': title},
            request=self.request
        )

class ManualProcessAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdministrator]

    def post(self, request, pk):
        manual = get_object_or_404(Manual, pk=pk)
        result = process_manual(manual.id, force_reprocess=True)
        return Response(result, status=status.HTTP_200_OK if result.get('status') == 'SUCCESS' else status.HTTP_400_BAD_REQUEST)

class ManualStatusAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        manual = get_object_or_404(Manual, pk=pk)
        return Response({
            'manual_id': str(manual.id),
            'title': manual.title,
            'machine_id': str(manual.machine_id),
            'processing_status': manual.processing_status,
            'page_count': manual.page_count,
            'chunk_count': manual.chunk_count,
            'error_message': manual.error_message,
            'updated_at': manual.updated_at
        })
