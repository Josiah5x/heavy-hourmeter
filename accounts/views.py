from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:index")

    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("dashboard:index")

    return render(
        request,
        "accounts/login.html",
        {"form": form},
    )


@login_required
def logout_view(request):
    logout(request)
    return redirect("accounts:login")


def register(request):
    return render(
        request,
        "accounts/register.html",
    )


@login_required
def profile(request):
    return render(
        request,
        "accounts/profile.html",
    )


@login_required
def password_change(request):
    return render(
        request,
        "accounts/password_change.html",
    )




@login_required
def logout_view(request):

    if request.method == "POST":
        logout(request)

    return redirect("accounts:login")