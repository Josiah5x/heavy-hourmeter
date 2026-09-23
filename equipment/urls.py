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
        name="detail",
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
]