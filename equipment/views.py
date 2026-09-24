from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EquipmentForm
from .models import Equipment


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