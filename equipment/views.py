from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EquipmentForm
from .models import Equipment

from .forms import ServiceRecordForm
from .models import Equipment, ServiceRecord



@login_required
def equipment_list(request):
    """
    Display all equipment available to the logged-in user.
    """

    equipment = (
        Equipment.objects
        .select_related("company", "site", "created_by")
        .all()
    )

    # --------------------------------------------------
    # SEARCH
    # --------------------------------------------------

    query = request.GET.get("q", "").strip()

    if query:
        equipment = equipment.filter(
            Q(asset_number__icontains=query)
            | Q(name__icontains=query)
            | Q(manufacturer__icontains=query)
            | Q(model__icontains=query)
            | Q(serial_number__icontains=query)
            | Q(registration_number__icontains=query)
        )


    # --------------------------------------------------
    # FILTER BY STATUS
    # --------------------------------------------------

    status = request.GET.get("status", "").strip()

    if status:
        equipment = equipment.filter(
            status=status
        )


    # --------------------------------------------------
    # FILTER BY TYPE
    # --------------------------------------------------

    equipment_type = request.GET.get(
        "equipment_type",
        ""
    ).strip()

    if equipment_type:
        equipment = equipment.filter(
            equipment_type=equipment_type
        )


    # --------------------------------------------------
    # FILTER BY COMPANY
    # --------------------------------------------------

    company = request.GET.get(
        "company",
        ""
    ).strip()

    if company:
        equipment = equipment.filter(
            company_id=company
        )


    # --------------------------------------------------
    # ORDERING
    # --------------------------------------------------

    equipment = equipment.order_by(
        "asset_number"
    )


    context = {
        "equipment": equipment,
        "query": query,
        "selected_status": status,
        "selected_type": equipment_type,
        "selected_company": company,

        "status_choices": Equipment.Status.choices,
        "equipment_types": Equipment.EquipmentType.choices,
    }

    return render(
        request,
        "equipment/equipment_list.html",
        context
    )


# ======================================================
# CREATE
# ======================================================

@login_required
def equipment_create(request):

    if request.method == "POST":

        form = EquipmentForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            equipment = form.save(
                commit=False
            )

            # Automatically record user
            equipment.created_by = request.user

            equipment.save()

            messages.success(
                request,
                (
                    f"{equipment.name} "
                    f"({equipment.asset_number}) "
                    "was registered successfully."
                )
            )

            return redirect(
                "equipment:detail",
                pk=equipment.pk
            )

    else:

        form = EquipmentForm()


    context = {
        "form": form,
        "object": None,
    }

    return render(
        request,
        "equipment/equipment_form.html",
        context
    )


# ======================================================
# DETAIL
# ======================================================

@login_required
def equipment_detail(request, pk):

    equipment = get_object_or_404(
        Equipment.objects.select_related(
            "company",
            "site",
            "created_by",
        ),
        pk=pk
    )

    context = {
        "equipment": equipment,
        "object": equipment,
    }

    return render(
        request,
        "equipment/equipment_detail.html",
        context
    )


# ======================================================
# UPDATE
# ======================================================

@login_required
def equipment_update(request, pk):

    equipment = get_object_or_404(
        Equipment,
        pk=pk
    )

    if request.method == "POST":

        form = EquipmentForm(
            request.POST,
            request.FILES,
            instance=equipment
        )

        if form.is_valid():

            equipment = form.save()

            messages.success(
                request,
                (
                    f"{equipment.name} "
                    f"was updated successfully."
                )
            )

            return redirect(
                "equipment:detail",
                pk=equipment.pk
            )

    else:

        form = EquipmentForm(
            instance=equipment
        )


    context = {
        "form": form,
        "object": equipment,
        "equipment": equipment,
    }

    return render(
        request,
        "equipment/equipment_form.html",
        context
    )


# ======================================================
# DELETE
# ======================================================

@login_required
def equipment_delete(request, pk):

    equipment = get_object_or_404(
        Equipment,
        pk=pk
    )

    if request.method == "POST":

        equipment_name = equipment.name
        asset_number = equipment.asset_number

        equipment.delete()

        messages.success(
            request,
            (
                f"{equipment_name} "
                f"({asset_number}) "
                "was deleted successfully."
            )
        )

        return redirect(
            "equipment:list"
        )


    context = {
        "equipment": equipment,
        "object": equipment,
    }

    return render(
        request,
        "equipment/equipment_confirm_delete.html",
        context
    )




from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from companies.models import Site

from .forms import ServiceRecordForm
from .models import ServiceRecord


# =========================================================
# SERVICE LIST
# =========================================================

@login_required
def service_list(request):

    services = (
        ServiceRecord.objects
        .select_related(
            "equipment",
            "equipment__company",
            "equipment__site",
            "created_by",
        )
        .all()
    )

    query = request.GET.get("q", "").strip()
    site = request.GET.get("site", "").strip()
    status = request.GET.get("status", "").strip()
    service_type = request.GET.get("service_type", "").strip()

    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    if query:

        services = services.filter(
            Q(equipment__asset_number__icontains=query)
            | Q(equipment__name__icontains=query)
            | Q(equipment__manufacturer__icontains=query)
            | Q(equipment__model__icontains=query)
            | Q(equipment__serial_number__icontains=query)
        )

    # -----------------------------------------------------
    # SITE
    # -----------------------------------------------------

    if site:

        services = services.filter(
            equipment__site_id=site
        )

    # -----------------------------------------------------
    # SERVICE TYPE
    # -----------------------------------------------------

    if service_type:

        services = services.filter(
            service_type=service_type
        )

    # -----------------------------------------------------
    # STATUS
    #
    # service_status is a Python property, so it cannot
    # be filtered directly by QuerySet.filter().
    # -----------------------------------------------------

    if status:

        matching_ids = []

        for service in services:

            if service.service_status == status:
                matching_ids.append(service.pk)

        services = services.filter(
            pk__in=matching_ids
        )

    # -----------------------------------------------------
    # STATISTICS
    # -----------------------------------------------------

    all_filtered_services = list(services)

    total = len(all_filtered_services)

    overdue = sum(
        1
        for service in all_filtered_services
        if service.service_status == "overdue"
    )

    due = sum(
        1
        for service in all_filtered_services
        if service.service_status == "due"
    )

    due_soon = sum(
        1
        for service in all_filtered_services
        if service.service_status == "due_soon"
    )

    not_due = sum(
        1
        for service in all_filtered_services
        if service.service_status == "not_due"
    )

    # -----------------------------------------------------
    # PAGINATION
    # -----------------------------------------------------

    paginator = Paginator(
        services,
        15,
    )

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(
        page_number
    )

    # -----------------------------------------------------
    # SITES
    # -----------------------------------------------------

    sites = (
        Site.objects
        .filter(is_active=True)
        .order_by("name")
    )

    # -----------------------------------------------------
    # CONTEXT
    # -----------------------------------------------------

    context = {
        "services": page_obj,
        "page_obj": page_obj,
        "paginator": paginator,

        "sites": sites,

        "total": total,
        "overdue": overdue,
        "due": due,
        "due_soon": due_soon,
        "not_due": not_due,

        "query": query,
        "selected_site": site,
        "selected_status": status,
        "selected_service_type": service_type,

        "service_types": (
            ServiceRecord.ServiceType.choices
        ),
    }

    return render(
        request,
        "equipment/service_list.html",
        context,
    )


# =========================================================
# CREATE SERVICE RECORD
# =========================================================

@login_required
def service_create(request):

    equipment_id = request.GET.get("equipment")

    if request.method == "POST":

        form = ServiceRecordForm(
            request.POST
        )

        if form.is_valid():

            service = form.save(
                commit=False
            )

            service.created_by = request.user

            service.save()

            messages.success(
                request,
                (
                    f"Service record for "
                    f"{service.equipment.asset_number} "
                    "created successfully."
                ),
            )

            return redirect(
                "equipment:service_detail",
                pk=service.pk,
            )

        # IMPORTANT:
        # If validation fails, stay on the page
        # and display form.errors.

    else:

        initial = {}

        if equipment_id:

            initial["equipment"] = equipment_id

        form = ServiceRecordForm(
            initial=initial
        )

    return render(
        request,
        "equipment/service_form.html",
        {
            "form": form,
            "service": None,
            "page_title": "Add Service Record",
            "submit_text": "Save Service Record",
        },
    )

# =========================================================
# SERVICE DETAIL
# =========================================================

@login_required
def service_detail(request, pk):

    service = get_object_or_404(
        ServiceRecord.objects.select_related(
            "equipment",
            "equipment__company",
            "equipment__site",
            "created_by",
        ),
        pk=pk,
    )

    return render(
        request,
        "equipment/service_detail.html",
        {
            "service": service,
        },
    )


# =========================================================
# UPDATE SERVICE RECORD
# =========================================================


@login_required
def service_update(request, pk):

    service = get_object_or_404(
        ServiceRecord,
        pk=pk,
    )

    if request.method == "POST":

        form = ServiceRecordForm(
            request.POST,
            instance=service,
        )

        if form.is_valid():

            service = form.save(
                commit=False
            )

            # Keep original creator
            # unless you specifically want to
            # change it during editing.

            service.save()

            messages.success(
                request,
                (
                    f"Service record for "
                    f"{service.equipment.asset_number} "
                    "updated successfully."
                ),
            )

            return redirect(
                "equipment:service_detail",
                pk=service.pk,
            )

    else:

        form = ServiceRecordForm(
            instance=service
        )

    return render(
        request,
        "equipment/service_form.html",
        {
            "form": form,
            "service": service,
            "page_title": "Edit Service Record",
            "submit_text": "Update Service Record",
        },
    )


# =========================================================
# DELETE SERVICE RECORD
# =========================================================

@login_required
def service_delete(request, pk):

    service = get_object_or_404(
        ServiceRecord,
        pk=pk,
    )

    if request.method == "POST":

        service.delete()

        messages.success(
            request,
            "Service record deleted successfully.",
        )

        return redirect(
            "equipment:service_list"
        )

    return render(
        request,
        "equipment/service_confirm_delete.html",
        {
            "service": service,
        },
    )

