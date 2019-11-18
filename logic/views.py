from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from logic.forms import UserForm
from datamodel import constants


def anonymous_required(f):
    def wrapped(request):
        if request.user.is_authenticated:
            return HttpResponseForbidden(
                errorHTTP(request, exception="Action restricted to anonymous users"))
        else:
            return f(request)
    return wrapped


def errorHTTP(request, exception=None):
    context_dict = {}
    context_dict[constants.ERROR_MESSAGE_ID] = exception
    return render(request, "mouse_cat/error.html", context_dict)

def index(request):
    return render(request, "mouse_cat/index.html")

@anonymous_required
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username, password) # DEBUG
        user_form = UserForm(data=request.POST)
        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            request.session['nickname'] = username
            return render(request, "mouse_cat/index.html")
        else:
            user_form.add_error('username', 'Username/password is not valid|Usuario/clave no válidos')
            print(user_form.errors)
            context_dict={'user_form': user_form}
            return render(request, "mouse_cat/login.html", context_dict)

    user_form = UserForm()
    context_dict={'user_form': user_form}
    return render(request, "mouse_cat/login.html", context_dict)

@login_required
def user_logout(request):
    context_dict = {'user': request.session.get('nickname')}
    logout(request)
    return render(request, "mouse_cat/logout.html", context_dict)


def signup(request):
    return render(request, "mouse_cat/signup.html")


def counter(request):
    return render(request, "mouse_cat/counter.html")


def create_game(request):
    return render(request, "mouse_cat/new_game.html")


def join_game(request):
    return render(request, "mouse_cat/join_game.html")


def select_game(request):
    return render(request, "mouse_cat/select_game.html")


def show_game(request):
    return render(request, "mouse_cat/game.html")


def move(request):
    pass
