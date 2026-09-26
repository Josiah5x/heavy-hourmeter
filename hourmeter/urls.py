from django.urls import path

from . import views


app_name = "hourmeter"


urlpatterns = [

    # Reading dashboard
    path(
        "list/",
        views.reading_list,
        name="reading_list",
    ),

    # Create
    path(
        "create/",
        views.reading_create,
        name="reading_create",
    ),


    path(
        "service-register/",
        views.service_register,
        name="service_register",
    ),

    # Detail
    path(
        "<int:pk>/",
        views.reading_detail,
        name="reading_detail",
    ),

    # Edit
    path(
        "<int:pk>/edit/",
        views.reading_update,
        name="reading_update",
    ),

    # Delete
    path(
        "<int:pk>/delete/",
        views.reading_delete,
        name="reading_delete",
    ),

    # Verify
    path(
        "<int:pk>/verify/",
        views.reading_verify,
        name="reading_verify",
    ),
]