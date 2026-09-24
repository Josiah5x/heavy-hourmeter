from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CompanyForm, SiteForm
from .models import Company, Site


# ============================================================
# COMPANY VIEWS
# ============================================================

@login_required
def company_list(request):
    """
    Display all companies with search and active/inactive filtering.
    """

    companies = (
        Company.objects
        .select_related("created_by")
        .prefetch_related("sites")
        .all()
    )

    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()

    # Search
    if query:
        companies = companies.filter(
            Q(name__icontains=query)
            | Q(short_name__icontains=query)
            | Q(address__icontains=query)
            | Q(phone__icontains=query)
            | Q(email__icontains=query)
        )

    # Status filter
    if status == "active":
        companies = companies.filter(is_active=True)

    elif status == "inactive":
        companies = companies.filter(is_active=False)

    companies = companies.order_by("name")

    context = {
        "companies": companies,
        "query": query,
        "selected_status": status,
    }

    return render(
        request,
        "companies/company_list.html",
        context,
    )


@login_required
def company_detail(request, pk):
    """
    Display company information and its sites.
    """

    company = get_object_or_404(
        Company.objects
        .select_related("created_by")
        .prefetch_related("sites"),
        pk=pk,
    )

    sites = company.sites.all().order_by("name")

    context = {
        "company": company,
        "sites": sites,
    }

    return render(
        request,
        "companies/company_detail.html",
        context,
    )


@login_required
def company_create(request):
    """
    Create a new company.
    """

    if request.method == "POST":
        form = CompanyForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            company = form.save(commit=False)

            company.created_by = request.user

            company.save()

            messages.success(
                request,
                f"{company.name} was created successfully.",
            )

            return redirect(
                "companies:company_detail",
                pk=company.pk,
            )

    else:
        form = CompanyForm()

    context = {
        "form": form,
        "object": None,
    }

    return render(
        request,
        "companies/company_form.html",
        context,
    )


@login_required
def company_update(request, pk):
    """
    Edit an existing company.
    """

    company = get_object_or_404(
        Company,
        pk=pk,
    )

    if request.method == "POST":
        form = CompanyForm(
            request.POST,
            request.FILES,
            instance=company,
        )

        if form.is_valid():
            company = form.save()

            messages.success(
                request,
                f"{company.name} was updated successfully.",
            )

            return redirect(
                "companies:company_detail",
                pk=company.pk,
            )

    else:
        form = CompanyForm(
            instance=company,
        )

    context = {
        "form": form,
        "object": company,
        "company": company,
    }

    return render(
        request,
        "companies/company_form.html",
        context,
    )


@login_required
def company_delete(request, pk):
    """
    Delete a company.

    Because Site has CASCADE on Company, deleting a company
    will also delete its sites and related equipment references
    may be affected depending on their ForeignKey configuration.
    """

    company = get_object_or_404(
        Company,
        pk=pk,
    )

    if request.method == "POST":
        company_name = company.name

        company.delete()

        messages.success(
            request,
            f"{company_name} was deleted successfully.",
        )

        return redirect(
            "companies:company_list",
        )

    return render(
        request,
        "companies/company_confirm_delete.html",
        {
            "company": company,
            "object": company,
        },
    )


# ============================================================
# SITE VIEWS
# ============================================================

@login_required
def site_list(request):
    """
    Display all sites with search and filtering.
    """

    sites = (
        Site.objects
        .select_related(
            "company",
            "created_by",
        )
        .all()
    )

    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    company_id = request.GET.get("company", "").strip()

    # Search
    if query:
        sites = sites.filter(
            Q(name__icontains=query)
            | Q(code__icontains=query)
            | Q(address__icontains=query)
            | Q(city__icontains=query)
            | Q(state__icontains=query)
            | Q(contact_person__icontains=query)
            | Q(contact_phone__icontains=query)
            | Q(company__name__icontains=query)
        )

    # Status
    if status == "active":
        sites = sites.filter(
            is_active=True
        )

    elif status == "inactive":
        sites = sites.filter(
            is_active=False
        )

    # Company filter
    if company_id:
        sites = sites.filter(
            company_id=company_id
        )

    sites = sites.order_by(
        "company__name",
        "name",
    )

    companies = Company.objects.filter(
        is_active=True
    ).order_by("name")

    context = {
        "sites": sites,
        "companies": companies,
        "query": query,
        "selected_status": status,
        "selected_company": company_id,
    }

    return render(
        request,
        "companies/site_list.html",
        context,
    )


@login_required
def site_detail(request, pk):
    """
    Display site details and equipment assigned to the site.
    """

    site = get_object_or_404(
        Site.objects.select_related(
            "company",
            "created_by",
        ),
        pk=pk,
    )

    # Equipment has related_name="equipment" on Site
    equipment = (
        site.equipment
        .select_related(
            "company",
            "site",
        )
        .order_by("asset_number")
    )

    context = {
        "site": site,
        "equipment": equipment,
    }

    return render(
        request,
        "companies/site_detail.html",
        context,
    )


@login_required
def site_create(request):
    """
    Create a new site.
    """

    if request.method == "POST":
        form = SiteForm(
            request.POST,
        )

        if form.is_valid():
            site = form.save(commit=False)

            site.created_by = request.user

            site.save()

            messages.success(
                request,
                f"{site.name} was created successfully.",
            )

            return redirect(
                "companies:site_detail",
                pk=site.pk,
            )

    else:
        form = SiteForm()

    context = {
        "form": form,
        "object": None,
    }

    return render(
        request,
        "companies/site_form.html",
        context,
    )


@login_required
def site_update(request, pk):
    """
    Edit an existing site.
    """

    site = get_object_or_404(
        Site,
        pk=pk,
    )

    if request.method == "POST":
        form = SiteForm(
            request.POST,
            instance=site,
        )

        if form.is_valid():
            site = form.save()

            messages.success(
                request,
                f"{site.name} was updated successfully.",
            )

            return redirect(
                "companies:site_detail",
                pk=site.pk,
            )

    else:
        form = SiteForm(
            instance=site,
        )

    context = {
        "form": form,
        "object": site,
        "site": site,
    }

    return render(
        request,
        "companies/site_form.html",
        context,
    )


@login_required
def site_delete(request, pk):
    """
    Delete a site.
    """

    site = get_object_or_404(
        Site.objects.select_related("company"),
        pk=pk,
    )

    if request.method == "POST":
        site_name = site.name
        company_name = site.company.name

        site.delete()

        messages.success(
            request,
            f"{site_name} ({company_name}) was deleted successfully.",
        )

        return redirect(
            "companies:site_list",
        )

    return render(
        request,
        "companies/site_confirm_delete.html",
        {
            "site": site,
            "object": site,
        },
    )