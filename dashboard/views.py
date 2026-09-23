from django.contrib.auth.decorators import login_required
from django.db.models import Sum

from django.shortcuts import render

from equipment.models import Equipment


@login_required
def dashboard(request):

    equipment = Equipment.objects.select_related(
        "company",
        "site",
    )

    equipment_count = equipment.count()

    active_equipment = equipment.filter(
        status=Equipment.Status.ACTIVE
    ).count()

    total_hours = equipment.aggregate(
        total=Sum("current_hours")
    )["total"] or 0

    attention_equipment = equipment.filter(
        status__in=[
            Equipment.Status.MAINTENANCE,
            Equipment.Status.OUT_OF_SERVICE,
        ]
    )[:10]

    context = {
        "equipment_count": equipment_count,
        "active_equipment": active_equipment,
        "total_hours": total_hours,
        "maintenance_due": 0,
        "attention_equipment": attention_equipment,
    }

    return render(
        request,
        "dashboard/index.html",
        context,
    )