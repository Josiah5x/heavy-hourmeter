from django.urls import path

from . import views


app_name = "equipment"


urlpatterns = [
    # Equipment dashboard/list
    path(
        "",
        views.equipment_list,
        name="list",
    ),

    # Create
    path(
        "create/",
        views.equipment_create,
        name="create",
    ),

    # Equipment details
    path(
        "<int:pk>/",
        views.equipment_detail,
        name="equipment_detail",
    ),

    # Edit
    path(
        "<int:pk>/edit/",
        views.equipment_update,
        name="update",
    ),

    # Delete
    path(
        "<int:pk>/delete/",
        views.equipment_delete,
        name="delete",
    ),



    # ============================================
    # SERVICE RECORDS
    # ============================================

    path(
        "services/",
        views.service_list,
        name="service_list",
    ),

    path(
        "services/create/",
        views.service_create,
        name="service_create",
    ),

    path(
        "services/<int:pk>/",
        views.service_detail,
        name="service_detail",
    ),

    path(
        "services/<int:pk>/edit/",
        views.service_update,
        name="service_update",
    ),

    path(
        "services/<int:pk>/delete/",
        views.service_delete,
        name="service_delete",
    ),
]
