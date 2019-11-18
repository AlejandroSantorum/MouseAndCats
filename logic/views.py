from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from logic.forms import UserForm, SignupForm
from datamodel import constants
from datamodel.models import Counter


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
        user_form = UserForm(data=request.POST)
        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            request.session['counter_session'] = 0
            return render(request, "mouse_cat/index.html")
        else:
            user_form.add_error('username', 'Username/password is not valid')
            context_dict={'user_form': user_form}
            return render(request, "mouse_cat/login.html", context_dict)

    user_form = UserForm()
    context_dict={'user_form': user_form}
    return render(request, "mouse_cat/login.html", context_dict)

@login_required
def user_logout(request):
    context_dict = {'user': request.user.username}
    request.session.pop('counter_session', None)
    logout(request)
    return render(request, "mouse_cat/logout.html", context_dict)

@anonymous_required
def signup(request):
    if request.method == 'POST':
        user_form = SignupForm(data=request.POST)
        if user_form.is_valid():
            cd = user_form.cleaned_data
        else:
            return render(request, "mouse_cat/signup.html", {'user_form': user_form})

        if cd['password'] != cd['password2']:
            user_form.add_error('password2', 'Password and Repeat password are not the same')
            return render(request, "mouse_cat/signup.html", {'user_form': user_form})

        try:
            validate_password(cd['password'])
        except ValidationError as err:
            user_form.add_error('password', ' '.join(err.messages))
            render(request, "mouse_cat/signup.html", {'user_form': user_form})

        try:
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            login(request, user)
            return render(request, "mouse_cat/index.html")
        except ValueError:
            return render(request, "mouse_cat/signup.html", {'user_form': user_form})

        return render(request, "mouse_cat/index.html")

    context_dict = {'user_form': SignupForm()}
    return render(request, "mouse_cat/signup.html", context_dict)


def counter(request):
    Counter.objects.inc()
    counter_global = Counter.objects.get_current_value()

    if not request.session.get('counter_session'):
        request.session['counter_session'] = 1
        counter_session = 1
    else:
        request.session['counter_session'] += 1
        counter_session = request.session['counter_session']

    context_dict={'counter_session': counter_session, 'counter_global': counter_global}
    return render(request, "mouse_cat/counter.html", context_dict)


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
