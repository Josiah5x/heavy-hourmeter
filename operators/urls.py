from django.urls import path

from . import views


app_name = "operators"


urlpatterns = [
    path(
        "",
        views.operator_list,
        name="list",
    ),

    path(
        "create/",
        views.operator_create,
        name="create",
    ),

    path(
        "<int:pk>/",
        views.operator_detail,
        name="detail",
    ),

    path(
        "<int:pk>/edit/",
        views.operator_update,
        name="update",
    ),

    path(
        "<int:pk>/delete/",
        views.operator_delete,
        name="delete",
    ),
]