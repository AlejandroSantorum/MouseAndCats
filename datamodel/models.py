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
    WIDTH = 8
    cat_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="games_as_cat")
    mouse_user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True,
                                   null=True, related_name="games_as_mouse")
    # Cat 1 position
    cat1 = models.IntegerField(validators=[
                                            MaxValueValidator(63),
                                            MinValueValidator(0)
                                          ],
                               default=0) # Not NULL is set by default
    # Cat 2 position
    cat2 = models.IntegerField(validators=[
                                            MaxValueValidator(63),
                                            MinValueValidator(0)
                                          ],
                               default=2)
    # Cat 3 position
    cat3 = models.IntegerField(validators=[
                                            MaxValueValidator(63),
                                            MinValueValidator(0)
                                          ],
                               default=4)
    # Cat 4 position
    cat4 = models.IntegerField(validators=[
                                            MaxValueValidator(63),
                                            MinValueValidator(0)
                                          ],
                               default=6)
    # Mouse position
    mouse = models.IntegerField(default=59)
    # true if it's cat's turn, false if it's mouse turn
    cat_turn = models.BooleanField(default=True)
    # Game status
    status = models.IntegerField(default=GameStatus.CREATED)

    # Game moves
    @property
    def moves(self):
        return Move.objects.filter(game=self)

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
        odd_col = bool((position//Game.WIDTH)%2)
        odd_row = bool((position%Game.WIDTH)%2)
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
    origin = models.IntegerField(validators=[
                                            MaxValueValidator(Game.MAX_CELL),
                                            MinValueValidator(Game.MIN_CELL)
                                          ])
    target = models.IntegerField(validators=[
                                            MaxValueValidator(Game.MAX_CELL),
                                            MinValueValidator(Game.MIN_CELL)
                                          ])
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=datetime.date.today)

    def __pos_to_list(self, position):
        return [(position//Game.WIDTH) + 1 , (position%Game.WIDTH) + 1]

    def __cat_valid_move(self):
        origin_lst = self.__pos_to_list(self.origin)
        target_lst = self.__pos_to_list(self.target)
        down_lst = [x+1 for x in origin_lst]
        if down_lst == target_lst:
            return True
        return False

    def __mouse_valid_move(self):
        origin_lst = self.__pos_to_list(self.origin)
        target_lst = self.__pos_to_list(self.target)
        down_lst = [x+1 for x in origin_lst]
        up_lst = [x-1 for x in origin_lst]
        if down_lst == target_lst:
            return True
        if up_lst == target_lst:
            return True
        return False

    def save(self, *args, **kwargs):
        if self.game.status != GameStatus.ACTIVE:
            raise ValidationError(MSG_ERROR_MOVE)
        if self.player == self.game.cat_user and not self.__cat_valid_move():
            raise ValidationError(MSG_ERROR_MOVE)
        if self.player == self.game.mouse_user and not self.__mouse_valid_move():
            raise ValidationError(MSG_ERROR_MOVE)
        super(Move, self).save(*args, **kwargs)
    # def __str__() TODO: Hacer para tests opcionales
