from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
import datetime


MSG_ERROR_INVALID_CELL = "Invalid cell for a cat or the mouse|"+\
                         "Gato o ratón en posición no válida"
MSG_ERROR_GAMESTATUS = "Game status not valid|Estado no válido"
MSG_ERROR_MOVE = "Move not allowed|Movimiento no permitido"
MSG_ERROR_NEW_COUNTER = "Insert not allowed|Inseción no permitida"

class GameStatus():
    CREATED = 0
    ACTIVE = 1
    FINISHED = 2


class Game(models.Model):
    MIN_CELL = 0
    MAX_CELL = 63
    cat_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="games_as_cat")
    mouse_user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True,
                                   null=True, related_name="games_as_mouse")
    # Cat 1 position
    cat1 = models.IntegerField(validators=[
                                            MaxValueValidator(MAX_CELL),
                                            MinValueValidator(MIN_CELL)
                                          ],
                               default=0) # Not NULL is set by default
    # Cat 2 position
    cat2 = models.IntegerField(validators=[
                                            MaxValueValidator(MAX_CELL),
                                            MinValueValidator(MIN_CELL)
                                          ],
                               default=2)
    # Cat 3 position
    cat3 = models.IntegerField(validators=[
                                            MaxValueValidator(MAX_CELL),
                                            MinValueValidator(MIN_CELL)
                                          ],
                               default=4)
    # Cat 4 position
    cat4 = models.IntegerField(validators=[
                                            MaxValueValidator(MAX_CELL),
                                            MinValueValidator(MIN_CELL)
                                          ],
                               default=6)
    # Mouse position
    mouse = models.IntegerField(default=59)
    # true if it's cat's turn, false if it's mouse turn
    cat_turn = models.BooleanField(default=True)
    # Game status
    status = models.IntegerField(default=GameStatus.CREATED)

    def __str_game_status(self):
        if self.status == 0:
            return "Created"
        elif self.status == 1:
            return "Active"
        else:
            return "Finished"

    def __pos_is_valid(self, position):
        if not position:
            return True
        odd_col = bool((position//8)%2)
        odd_row = bool((position%8)%2)
        return not (odd_col ^ odd_row)

    def clean(self, exclude=None):
        # Validators for cat not null and cell's range are already
        # defined in model definition
        if self.status == GameStatus.CREATED and self.mouse_user != None:
            raise ValidationError(MSG_ERROR_GAMESTATUS)
        if self.status == GameStatus.ACTIVE and not self.mouse_user:
            raise ValidationError(MSG_ERROR_GAMESTATUS)
        if self.status == GameStatus.FINISHED and not self.mouse_user:
            raise ValidationError(MSG_ERROR_GAMESTATUS)

    def save(self, *args, **kwargs): #TODO: Decide if this calls clean or not
        if self.mouse_user and self.status == GameStatus.CREATED:
            self.status = GameStatus.ACTIVE
        # Validations for test10 (valid cells) below:
        if not self.__pos_is_valid(self.cat1):
            raise ValidationError(MSG_ERROR_INVALID_CELL)
        if not self.__pos_is_valid(self.cat2):
            raise ValidationError(MSG_ERROR_INVALID_CELL)
        if not self.__pos_is_valid(self.cat3):
            raise ValidationError(MSG_ERROR_INVALID_CELL)
        if not self.__pos_is_valid(self.cat4):
            raise ValidationError(MSG_ERROR_INVALID_CELL)
        if not self.__pos_is_valid(self.mouse):
            raise ValidationError(MSG_ERROR_INVALID_CELL)
        super(Game, self).save(*args, **kwargs)


    def __str__(self):
        id = str(self.id)
        status = self.__str_game_status()
        if self.cat_turn:
            c_turn = "[X]"
            m_turn = "[ ]"
        else:
            c_turn = "[ ]"
            m_turn = "[X]"

        c_pos = "("+str(self.cat1)+", "+str(self.cat2)+", "+str(self.cat3)+", "+str(self.cat4)+")"
        if not self.mouse_user:
            ret_str = "("+id+", "+status+")\tCat "+c_turn+" cat_user_test"+c_pos
            return ret_str

        m_pos = "("+str(self.mouse)+")"
        ret_str = "("+id+", "+status+")\tCat "+c_turn+" cat_user_test"+c_pos+\
               " --- Mouse "+m_turn+" mouse_user_test"+m_pos
        return ret_str


class Counter(models.Model):
    pass


class Move(models.Model):
    # def __game_active_validator(game):
    #     if game.status != GameStatus.ACTIVE:
    #         return false
    #
    # origin = models.IntegerField()
    # target = models.IntegerField()
    # game = models.ForeignKey(Game, on_delete=models.CASCADE)
    # player = models.ForeignKey(User, on_delete=models.CASCADE)
    # date = models.DateField(default=datetime.date.today)
    #
    # def __pos_is_valid(self, position):
    #     if not position:
    #         return False
    #     odd_col = bool((position//8)%2)
    #     odd_row = bool((position%8)%2)
    #     return not (odd_col ^ odd_row)
    #
    # def clean_fields(self, exclude=None):
    #     if not self.__pos_is_valid(self.origin) or not\
    #     self.__pos_is_valid(self.target):
    #         raise ValidationError(MSG_ERROR_MOVE)
    #
    # def save(self, *args, **kwargs):
    #     self.clean_fields()
    #     super(Move, self).save(*args, **kwargs)
    pass
    # def __str__() TODO: Hacer para tests opcionales
