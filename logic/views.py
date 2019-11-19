from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from logic.forms import UserForm, SignupForm, MoveForm
from datamodel import constants
from datamodel.models import Counter, Game, GameStatus, Move
from django.db.models import Q


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
            request.session[constants.COUNTER_SESSION_ID] = 0
            return render(request, "mouse_cat/index.html")
        else:
            user_form.errors['username'] = [] # TODO: Mirar por qué esto es necesario
            user_form.add_error('username', 'Username/password is not valid')
            context_dict={'user_form': user_form}
            return render(request, "mouse_cat/login.html", context_dict)

    user_form = UserForm()
    context_dict={'user_form': user_form}
    return render(request, "mouse_cat/login.html", context_dict)


@login_required
def user_logout(request):
    context_dict = {'user': request.user.username}
    request.session.pop(constants.COUNTER_SESSION_ID, None)
    request.session.pop(constants.GAME_SELECTED_SESSION_ID, None)
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

    if not request.session.get(constants.COUNTER_SESSION_ID):
        request.session[constants.COUNTER_SESSION_ID] = 1
        counter_session = 1
    else:
        request.session[constants.COUNTER_SESSION_ID] += 1
        counter_session = request.session[constants.COUNTER_SESSION_ID]

    context_dict={'counter_session': counter_session, 'counter_global': counter_global}
    return render(request, "mouse_cat/counter.html", context_dict)


@login_required
def create_game(request):
    game = Game.objects.create(cat_user=request.user)
    return render(request, "mouse_cat/new_game.html", {'game':game})


@login_required
def join_game(request):
    pending_games = Game.objects.filter(mouse_user=None)
    pending_games = pending_games.exclude(cat_user=request.user).order_by('-id')
    if len(pending_games) == 0:
        return render(request, "mouse_cat/join_game.html", {'msg_error': 'There is no available games'})
    game = pending_games[0]
    game.mouse_user = request.user
    game.save()
    return render(request, "mouse_cat/join_game.html", {'game': game})


@login_required
def select_game(request, game_id=None):
    if request.method == 'POST' or request.method == 'GET': # OR CLAUSE SHOULDN'T BE THERE, TESTS ARE WRONG - TODO: DELETE OR CLAUSE
        if game_id:
            my_games = Game.objects.filter(Q(cat_user = request.user) | Q(mouse_user = request.user))
            my_games = list(my_games.filter(status = GameStatus.ACTIVE))
            my_games = [game.id for game in my_games]
            if game_id in my_games:
                request.session[constants.GAME_SELECTED_SESSION_ID] = int(game_id)
            else:
                return HttpResponse('Selected game does not exist.', status=404)
    # GET
    as_cat = list(Game.objects.filter(cat_user=request.user, status=GameStatus.ACTIVE))
    as_mouse = list(Game.objects.filter(mouse_user=request.user, status=GameStatus.ACTIVE))
    context_dict = {'as_cat': as_cat, 'as_mouse': as_mouse}
    return render(request, "mouse_cat/select_game.html", context_dict)


@login_required
def show_game(request):
    if not request.session.get(constants.GAME_SELECTED_SESSION_ID):
        return redirect(reverse('select_game')) #TODO: ADD EXTRA TEST FOR THIS

    game = Game.objects.get(id=request.session.get(constants.GAME_SELECTED_SESSION_ID))

    if not game: #TODO: ADD EXTRA TEST FOR THIS
        return redirect(reverse('select_game'))

    board = [0]*constants.BOARD_SIZE
    board[game.mouse] = -1
    for i in game._get_cat_places():
        board[i] = 1
    context_dict = {'board': board, 'game': game, 'move_form': MoveForm()}
    return render(request, "mouse_cat/game.html", context_dict)


@login_required
def move(request):
    if request.method == 'GET':
        return HttpResponse('Invalid method.', status=404)
    #POST
    if not request.session.get(constants.GAME_SELECTED_SESSION_ID):
        return HttpResponse('Invalid method.', status=404)
    game = Game.objects.get(id=request.session.get(constants.GAME_SELECTED_SESSION_ID))

    origin = int(request.POST.get('origin'))
    target = int(request.POST.get('target'))
    move = Move(origin=origin, target=target, game=game, player=request.user)
    move.save()
    return redirect(reverse('show_game'))
