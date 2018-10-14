import itertools
from GameObjects import *
from pygame.locals import *

# grid functions, main functions
# Tetrimino class is built to create the object for main so that it could execute
# Tetrimino class is the object, Grid is the manipulator


class Grid(GameRect):
    def __init__(self, surface, x, y, square_x, square_y, square_size=10, forecolor=Colors.WHITE, bgcolor=Colors.BLACK, rectwidth=5):
        GameRect.__init__(self, surface, x, y, rectwidth + 3 + square_x * square_size, rectwidth + 3 + square_y * square_size, forecolor=forecolor, bgcolor=bgcolor, rectwidth=rectwidth)
        self.__matrix = [[Block(self._surface, self.x + rectwidth - 1 + i * square_size, self.y - 1 + rectwidth + j * square_size, length=square_size, color=bgcolor, bgcolor=bgcolor) for i in range(square_x)] for j in range(square_y)]
        self.tetromino = None

    # display the blocks
    def drawblocks(self):
        for obj in itertools.chain.from_iterable(zip(*self.__matrix)):
            obj.redraw()

    # have absolutely no idea wtf this does
    def draw_tetromino(self):
        assert self.tetromino, 'There is no Tetromino.'
        self.tetromino > self.__matrix

    # drop upperblock when one is fixed
    def __drop_upperblocks(self, line):
        for _line, _prev_line in zip(self.__matrix[self.__matrix.index(line):0:-1],
                                     self.__matrix[self.__matrix.index(line)::-1][1:]):
            for obj, prev_obj in zip(_line, _prev_line):
                obj.changecolor(prev_obj.getcolor())
                obj.falling = False

    # lock in place when down or paused
    def __freeze(self):
        for obj in itertools.chain.from_iterable(zip(*self.__matrix)):
            obj.falling = False

    # clear
    def erase_tetromino(self):
        assert self.tetromino, 'There is no Tetromino.'
        for i, j in itertools.product([self.tetromino.i + x for x in range(4)],
                                      [self.tetromino.j + x for x in range(4)]):
            try:
                if self.__matrix[i][j].falling: self.__matrix[i][j].changecolor(self._bgcolor)
            except IndexError: pass

    # flashes when one line is completed
    def __flashline(self, line):
        for t in range(2):
            for obj in line: obj.changecolor(Colors.WHITE)
            self.drawblocks()
            time.sleep(0.2)
            for obj in line: obj.changecolor(self._bgcolor)
            self.drawblocks()
            time.sleep(0.2)

    # check if the entire line is filled
    def check_lines(self):
        score = 0
        for line in self.__matrix:
            for obj in line:
                if obj.empty():
                    break
            else:
                self.__flashline(line)
                self.dropblocks()
                score += 1
        return score

    # check if the tetrimino object is at the border
    def tetromino_at_the_border(self, border):
        return self.tetromino.at_the_border(self.__matrix, border)

    # movements, shifting matrices
    def move_tetromino(self, direction):
        assert self.tetromino, 'There is no Tetromino.'
        if direction == K_LEFT:
            self.tetromino.j -= 1
        elif direction == K_DOWN:
            self.tetromino.i += 1
        elif direction == K_UP:
            self.tetromino.i -= 1
        elif direction == K_RIGHT:
            self.tetromino.j += 1

    # rotate tetrimino object
    def rotate_tetromino(self):
        self.tetromino.rotate()

    # hard drop with space
    def harddrop(self):
        if self.tetromino:
            self.erase_tetromino()
            while not self.tetromino.check_collision(self.__matrix):
                self.move_tetromino(K_DOWN)
            else:
                self.move_tetromino(K_UP)
                self.draw_tetromino()
                self.__freeze()
                self.tetromino = None

    def dropblocks(self):
        # if it's used on object tetrimino drop
        if self.tetromino:
            self.erase_tetromino()
            self.move_tetromino(K_DOWN)
            if not self.tetromino.check_collision(self.__matrix):
                self.draw_tetromino()
            else:
                self.move_tetromino(K_UP)
                self.draw_tetromino()
                self.__freeze()
                self.tetromino = None
        else:
            # if it's not used on object, drop all blocks down
            for line, prev_line in zip(self.__matrix[:0:-1], self.__matrix[::-1][1:]):
                for obj, prev_obj in zip(line, prev_line):
                    if not obj.empty(): break
                else:
                    self.__drop_upperblocks(line)


# Tetromino class is the object that Grid will be using
class Tetromino(object):
    def __init__(self, i, j, figure):
        self.__figure = list(figure[0])
        self.i = i
        self.j = j
        self.color = figure[1]

    def __gt__(self, otherobj):

        assert not self.check_collision(otherobj), 'There is another block here!'
        for i, j in itertools.product([self.i + x for x in range(4)], [self.j + x for x in range(4)]):
            if self.__figure[i - self.i][j - self.j]:
                otherobj[i][j].changecolor(self.color)
        return otherobj

    # check if tetromino is about to hit other tetromino or the ground
    def check_collision(self, matrix):
        for i, j in itertools.product([self.i + x for x in range(4)], [self.j + x for x in range(4)]):
            if self.__figure[i - self.i][j - self.j]:
                if i >= len(matrix): return True
                try:
                    if not matrix[i][j].empty():
                        return True
                except IndexError: pass
        else: return False

    # check if tetromino is at the border
    def at_the_border(self, matrix, border):
        border_limit = 0
        if border == K_LEFT:
            border_limit = 0
        elif border == K_RIGHT:
            border_limit = (len(matrix[0]) - 1)
        for i, j in itertools.product([self.i + x for x in range(4)], [self.j + x for x in range(4)]):
            if self.__figure[i - self.i][j - self.j]:
                try:
                    if j == border_limit: return True
                    elif (not matrix[i][j + (1 if border == K_RIGHT else -1)].empty() and not matrix[i][
                        j + (1 if border == K_RIGHT else -1)].falling): return True
                except IndexError: pass
        else: return False

    # rotate the tetromino
    def rotate(self):
        self.__figure = list(zip(*self.__figure[::-1]))