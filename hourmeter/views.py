from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import HourMeterReadingForm
from .models import HourMeterReading

from equipment.models import Equipment


# ============================================================
# DASHBOARD
# ============================================================

@login_required
def dashboard(request):

    readings = HourMeterReading.objects.select_related(
        "equipment",
        "site",
        "recorded_by",
        "verified_by",
    )

    total_readings = readings.count()

    today = timezone.localdate()

    today_readings = readings.filter(
        reading_date=today
    ).count()

    total_hours = readings.aggregate(
        total=Sum("hours_worked")
    )["total"] or Decimal("0.0")

    unverified_readings = readings.filter(
        is_verified=False
    ).count()

    recent_readings = readings.order_by(
        "-reading_date",
        "-created_at",
    )[:10]


    # --------------------------------------------------------
    # SERVICE STATUS
    # --------------------------------------------------------

    service_queryset = []

    for equipment in Equipment.objects.all():

        latest_service = getattr(
            equipment,
            "service_records",
            None
        )

        if latest_service is None:
            continue

        latest_service = latest_service.order_by(
            "-service_date"
        ).first()

        if latest_service:
            service_queryset.append(latest_service)


    overdue = 0
    due_soon = 0
    not_due = 0

    for service in service_queryset:

        current_hm = (
            Equipment.objects
            .filter(pk=service.equipment_id)
            .values_list("current_hours", flat=True)
            .first()
            or Decimal("0")
        )

        remaining = (
            service.next_service - current_hm
        )

        if remaining <= 0:

            overdue += 1

        elif remaining <= 50:

            due_soon += 1

        else:

            not_due += 1


    total_service = (
        overdue +
        due_soon +
        not_due
    )


    if total_service:

        overdue_percent = (
            overdue / total_service
        ) * 100

        due_soon_percent = (
            due_soon / total_service
        ) * 100

        not_due_percent = (
            not_due / total_service
        ) * 100

    else:

        overdue_percent = 0
        due_soon_percent = 0
        not_due_percent = 0


    context = {

        "total_readings": total_readings,

        "today_readings": today_readings,

        "total_hours": total_hours,

        "unverified_readings": unverified_readings,

        "recent_readings": recent_readings,

        "overdue": overdue,

        "due_soon": due_soon,

        "not_due": not_due,

        "overdue_percent": overdue_percent,

        "due_soon_percent": due_soon_percent,

        "not_due_percent": not_due_percent,
    }

    return render(
        request,
        "hourmeter/dashboard.html",
        context,
    )


# ============================================================
# READING LIST
# ============================================================

@login_required
def reading_list(request):

    readings = HourMeterReading.objects.select_related(
        "equipment",
        "site",
        "recorded_by",
    )

    # Search

    query = request.GET.get("q", "").strip()

    if query:

        readings = readings.filter(
            Q(equipment__name__icontains=query)
            |
            Q(equipment__asset_number__icontains=query)
            |
            Q(operator_name__icontains=query)
        )


    # Reading type

    reading_type = request.GET.get(
        "reading_type"
    )

    if reading_type:

        readings = readings.filter(
            reading_type=reading_type
        )


    # Verification

    verified = request.GET.get(
        "verified"
    )

    if verified == "yes":

        readings = readings.filter(
            is_verified=True
        )

    elif verified == "no":

        readings = readings.filter(
            is_verified=False
        )


    paginator = Paginator(
        readings,
        25
    )

    page_number = request.GET.get(
        "page"
    )

    page_obj = paginator.get_page(
        page_number
    )


    context = {

        "page_obj": page_obj,

        "reading_types":
            HourMeterReading.ReadingType.choices,
    }

    return render(
        request,
        "hourmeter/reading_list.html",
        context,
    )


# ============================================================
# ADD READING
# ============================================================

@login_required
def reading_create(request):

    if request.method == "POST":

        form = HourMeterReadingForm(
            request.POST
        )

        if form.is_valid():

            reading = form.save(
                commit=False
            )

            reading.recorded_by = request.user

            reading.save()


            # Update equipment current HM

            equipment = reading.equipment

            if (
                equipment.current_hours is None
                or
                reading.current_reading >
                equipment.current_hours
            ):

                equipment.current_hours = (
                    reading.current_reading
                )

                equipment.save(
                    update_fields=[
                        "current_hours",
                        "updated_at",
                    ]
                )


            messages.success(
                request,
                "Hour-meter reading recorded successfully."
            )

            return redirect(
                "hourmeter:reading_detail",
                reading.pk
            )

    else:

        form = HourMeterReadingForm()


    return render(
        request,
        "hourmeter/reading_form.html",
        {
            "form": form
        }
    )


# ============================================================
# EDIT READING
# ============================================================

@login_required
def reading_update(request,pk):

    reading = get_object_or_404(
        HourMeterReading,
        pk=pk
    )


    if request.method == "POST":

        form = HourMeterReadingForm(
            request.POST,
            instance=reading
        )

        if form.is_valid():

            reading = form.save()

            messages.success(
                request,
                "Hour-meter reading updated successfully."
            )

            return redirect(
                "hourmeter:reading_detail",
                reading.pk
            )

    else:

        form = HourMeterReadingForm(
            instance=reading
        )


    return render(
        request,
        "hourmeter/reading_form.html",
        {
            "form": form,
            "reading": reading,
        }
    )


# ============================================================
# READING DETAIL
# ============================================================

@login_required
def reading_detail(request,pk):

    reading = get_object_or_404(
        HourMeterReading.objects.select_related(
            "equipment",
            "site",
            "recorded_by",
            "verified_by",
        ),
        pk=pk,
    )


    context = {

        "reading": reading,

        "can_verify": (
            not reading.is_verified
        ),
    }


    return render(
        request,
        "hourmeter/reading_detail.html",
        context,
    )


# ============================================================
# DELETE READING
# ============================================================

@login_required
def reading_delete(request,pk):

    reading = get_object_or_404(
        HourMeterReading,
        pk=pk
    )


    if request.method == "POST":

        equipment = reading.equipment

        reading.delete()


        # Restore latest equipment reading

        latest = (
            HourMeterReading.objects
            .filter(
                equipment=equipment
            )
            .order_by(
                "-reading_date",
                "-created_at",
            )
            .first()
        )


        if latest:

            equipment.current_hours = (
                latest.current_reading
            )

        else:

            equipment.current_hours = Decimal(
                "0.0"
            )


        equipment.save(
            update_fields=[
                "current_hours",
                "updated_at",
            ]
        )


        messages.success(
            request,
            "Hour-meter reading deleted successfully."
        )

        return redirect(
            "hourmeter:reading_list"
        )


    return render(
        request,
        "hourmeter/reading_confirm_delete.html",
        {
            "reading": reading
        }
    )


# ============================================================
# VERIFY READING
# ============================================================

@login_required
def reading_verify(request,pk):

    reading = get_object_or_404(
        HourMeterReading,
        pk=pk
    )


    if request.method == "POST":

        reading.is_verified = True

        reading.verified_by = request.user

        reading.verified_at = timezone.now()

        reading.save(
            update_fields=[
                "is_verified",
                "verified_by",
                "verified_at",
                "updated_at",
            ]
        )


        messages.success(
            request,
            "Hour-meter reading verified successfully."
        )


    return redirect(
        "hourmeter:reading_detail",
        reading.pk
    )



@login_required
def service_register(request):

    query = request.GET.get("q", "").strip()
    site_id = request.GET.get("site", "").strip()
    service_type = request.GET.get(
        "service_type",
        "",
    ).strip()

    services = (
        ServiceRecord.objects
        .select_related(
            "equipment",
            "equipment__site",
            "equipment__company",
        )
        .all()
    )

    # --------------------------------------------------
    # SEARCH
    # --------------------------------------------------

    if query:

        services = services.filter(
            Q(equipment__name__icontains=query)
            | Q(
                equipment__asset_number__icontains=query
            )
            | Q(
                equipment__manufacturer__icontains=query
            )
            | Q(
                equipment__model__icontains=query
            )
        )

    # --------------------------------------------------
    # SITE
    # --------------------------------------------------

    if site_id:

        services = services.filter(
            equipment__site_id=site_id
        )

    # --------------------------------------------------
    # SERVICE TYPE
    # --------------------------------------------------

    if service_type:

        services = services.filter(
            service_type=service_type
        )

    services = services.order_by(
        "equipment__asset_number"
    )

    # --------------------------------------------------
    # CREATE REGISTER ROWS
    # --------------------------------------------------

    rows = []

    for service in services:

        current_hm = service.current_hm

        remaining = (
            service.next_service
            - current_hm
        )

        if remaining <= 0:
            status = "overdue"

        elif remaining <= 50:
            status = "due"

        elif remaining <= 100:
            status = "due_soon"

        else:
            status = "not_due"

        rows.append({
            "service": service,

            "machine": (
                service.equipment.name
            ),

            "location": (
                service.equipment.site.name
                if service.equipment.site
                else "—"
            ),

            "fleet_number": (
                service.equipment.asset_number
            ),

            "service_type": (
                service.get_service_type_display()
            ),

            "date": service.service_date,

            "hm_at_service": (
                service.hour_meter_at_service
            ),

            "next_service": (
                service.next_service
            ),

            "current_hm": current_hm,

            "remaining": remaining,

            "service_status": status,

            "air_filter": (
                service.get_air_filter_status_display()
            ),
        })

    # --------------------------------------------------
    # FILTER DATA
    # --------------------------------------------------

    sites = (
        Site.objects
        .filter(is_active=True)
        .order_by("name")
    )

    context = {
        "rows": rows,

        "sites": sites,

        "service_types": (
            ServiceRecord.ServiceType.choices
        ),

        "query": query,

        "selected_site": site_id,

        "selected_service_type": (
            service_type
        ),

        "total": len(rows),

        "overdue": sum(
            row["service_status"] == "overdue"
            for row in rows
        ),

        "due": sum(
            row["service_status"] == "due"
            for row in rows
        ),

        "due_soon": sum(
            row["service_status"] == "due_soon"
            for row in rows
        ),

        "not_due": sum(
            row["service_status"] == "not_due"
            for row in rows
        ),
    }

    return render(
        request,
        "hourmeter/service_register.html",
        context,
    )



