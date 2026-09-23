from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Operator


@login_required
def operator_list(request):
    operators = Operator.objects.select_related(
        "company",
        "site",
        "user",
    )

    return render(
        request,
        "operators/operator_list.html",
        {"operators": operators},
    )


@login_required
def operator_create(request):
    return render(
        request,
        "operators/operator_form.html",
    )


@login_required
def operator_detail(request, pk):
    operator = get_object_or_404(
        Operator.objects.select_related(
            "company",
            "site",
            "user",
        ),
        pk=pk,
    )

    return render(
        request,
        "operators/operator_detail.html",
        {"operator": operator},
    )


@login_required
def operator_update(request, pk):
    operator = get_object_or_404(
        Operator,
        pk=pk,
    )

    return render(
        request,
        "operators/operator_form.html",
        {"operator": operator},
    )


@login_required
def operator_delete(request, pk):
    operator = get_object_or_404(
        Operator,
        pk=pk,
    )

    if request.method == "POST":
        operator.delete()
        return redirect("operators:list")

    return render(
        request,
        "operators/operator_confirm_delete.html",
        {"operator": operator},
    )