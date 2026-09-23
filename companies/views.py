from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Company, Site


@login_required
def company_list(request):
    companies = Company.objects.all()

    return render(
        request,
        "companies/company_list.html",
        {"companies": companies},
    )


@login_required
def company_create(request):
    return render(
        request,
        "companies/company_form.html",
    )


@login_required
def company_detail(request, pk):
    company = get_object_or_404(Company, pk=pk)

    return render(
        request,
        "companies/company_detail.html",
        {"company": company},
    )


@login_required
def company_update(request, pk):
    company = get_object_or_404(Company, pk=pk)

    return render(
        request,
        "companies/company_form.html",
        {"company": company},
    )


@login_required
def company_delete(request, pk):
    company = get_object_or_404(Company, pk=pk)

    if request.method == "POST":
        company.delete()
        return redirect("companies:list")

    return render(
        request,
        "companies/company_confirm_delete.html",
        {"company": company},
    )


@login_required
def site_list(request):
    sites = Site.objects.select_related("company")

    return render(
        request,
        "companies/site_list.html",
        {"sites": sites},
    )


@login_required
def site_create(request):
    return render(
        request,
        "companies/site_form.html",
    )


@login_required
def site_detail(request, pk):
    site = get_object_or_404(Site, pk=pk)

    return render(
        request,
        "companies/site_detail.html",
        {"site": site},
    )


@login_required
def site_update(request, pk):
    site = get_object_or_404(Site, pk=pk)

    return render(
        request,
        "companies/site_form.html",
        {"site": site},
    )


@login_required
def site_delete(request, pk):
    site = get_object_or_404(Site, pk=pk)

    if request.method == "POST":
        site.delete()
        return redirect("companies:site_list")

    return render(
        request,
        "companies/site_confirm_delete.html",
        {"site": site},
    )