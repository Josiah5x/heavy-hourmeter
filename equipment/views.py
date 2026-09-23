from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Equipment


@login_required
def equipment_list(request):
    equipment = Equipment.objects.select_related(
        "company",
        "site",
    )

    return render(
        request,
        "equipment/equipment_list.html",
        {"equipment": equipment},
    )


@login_required
def equipment_create(request):
    return render(
        request,
        "equipment/equipment_form.html",
    )


@login_required
def equipment_detail(request, pk):
    item = get_object_or_404(
        Equipment.objects.select_related(
            "company",
            "site",
        ),
        pk=pk,
    )

    return render(
        request,
        "equipment/equipment_detail.html",
        {"equipment": item},
    )


@login_required
def equipment_update(request, pk):
    item = get_object_or_404(
        Equipment,
        pk=pk,
    )

    return render(
        request,
        "equipment/equipment_form.html",
        {"equipment": item},
    )


@login_required
def equipment_delete(request, pk):
    item = get_object_or_404(
        Equipment,
        pk=pk,
    )

    if request.method == "POST":
        item.delete()
        return redirect("equipment:list")

    return render(
        request,
        "equipment/equipment_confirm_delete.html",
        {"equipment": item},
    )