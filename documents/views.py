from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods
from .forms import UploadForm
from .models import Document
from .services.import_csv import save_records

@login_required
@require_GET
def document_list(request):
    documents = Document.objects.filter(owner=request.user)
    page = Paginator(documents, 25).get_page(request.GET.get("page"))
    return render(request, "documents/list.html", {"page": page})

@login_required
@require_GET
def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk, owner=request.user)
    return render(request, "documents/detail.html", {"document": document})

@login_required
@require_http_methods(["GET", "POST"])
def upload(request):
    form = UploadForm(request.POST, request.FILES) if request.method == "POST" else UploadForm()
    if request.method == "POST" and form.is_valid():
        try:
            count = save_records(form.records, request.user)
        except ValidationError:
            form.add_error("file", "The records could not be validated. Nothing was imported.")
        else:
            messages.success(request, f"Imported {count} document(s).")
            return redirect("documents:list")
    return render(request, "documents/upload.html", {"form": form})

@login_required
@require_GET
def example_csv(request):
    response = HttpResponse("title,abstract,source\nSynthetic TCM example,Demonstration text only,Fictional source\n", content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="example.csv"'
    return response
