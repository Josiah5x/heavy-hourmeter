from django.urls import path

from . import views


app_name = "companies"


urlpatterns = [
    # Companies
    path(
        "",
        views.company_list,
        name="list",
    ),

    path(
        "create/",
        views.company_create,
        name="create",
    ),

    path(
        "<int:pk>/",
        views.company_detail,
        name="detail",
    ),

    path(
        "<int:pk>/edit/",
        views.company_update,
        name="update",
    ),

    path(
        "<int:pk>/delete/",
        views.company_delete,
        name="delete",
    ),

    # Sites
    path(
        "sites/",
        views.site_list,
        name="site_list",
    ),

    path(
        "sites/create/",
        views.site_create,
        name="site_create",
    ),

    path(
        "sites/<int:pk>/",
        views.site_detail,
        name="site_detail",
    ),

    path(
        "sites/<int:pk>/edit/",
        views.site_update,
        name="site_update",
    ),

    path(
        "sites/<int:pk>/delete/",
        views.site_delete,
        name="site_delete",
    ),
]