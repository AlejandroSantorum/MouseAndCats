from django import forms
from django.contrib.auth.models import User
from datamodel.models import Move, Game
from django.core.validators import MaxValueValidator, MinValueValidator

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'password')

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'password')

class MoveForm(forms.ModelForm):
    origin = forms.IntegerField(validators=[
                                            MaxValueValidator(Game.MAX_CELL),
                                            MinValueValidator(Game.MIN_CELL)
                                          ])
    target = forms.IntegerField(validators=[
                                            MaxValueValidator(Game.MAX_CELL),
                                            MinValueValidator(Game.MIN_CELL)
                                          ])

    class Meta:
        model = Move
        fields = ('origin', 'target')
