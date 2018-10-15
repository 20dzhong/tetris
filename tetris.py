from GameObjects import *
from pygame.locals import *
import pygame
import sys
import random
import sets

# TODO hard drop highlight
# TODO add highlight to show hard drop location
# TODO make a Time display

window_width = 800
window_height = 650
window_x = 5
window_y = 5


# declare tetromino shapes
class Shapes:
    LINE = ([[False, False, True, False]] * 4, Colors.CYAN)
    SQUARE = ([[False] * 4, [False, True, True, False], [False, True, True, False], [False] * 4], Colors.YELLOW)
    L_1 = ([[False, False, False, False]] + [[False, False, True, False]] * 2 + [[False, True, True, False]], Colors.BLUE)
    L_2 = ([[False, False, False, False]] + [[False, True, False, False]] * 2 + [[False, True, True, False]], Colors.ORANGE)
    S_1 = ([[False] * 4] + [[False, False, True, True], [False, True, True, False]] + [[False] * 4], Colors.GREEN)
    S_2 = ([[False] * 4] + [[True, True, False, False], [False, True, True, False]] + [[False] * 4], Colors.RED)
    FORK = ([[False] * 4] + [[False, False, True, False], [False, True, True, True]] + [[False] * 4], Colors.PURPLE)
    ACTIONSQUARE = ([[True] * 4] * 4, Colors.RED)


# close everything
def terminate(grid):
    pygame.mixer.music.stop()
    pygame.quit()
    sys.exit()


# generate random tetromino
def random_tetromino():
    return getattr(Shapes, random.choice(['LINE', 'SQUARE', 'L_1', 'L_2', 'S_1', 'S_2', 'FORK']))


# display game over
def display_game_over(screen):
    display = Text(screen, 25, 205, fontcolor=Colors.WHITE, legend='GAME OVER')
    display.draw()

    option1 = Text(screen, 25, 265, fontcolor=Colors.WHITE, fontsize=20, legend='Press Q to quit')
    option2 = Text(screen, 25, 295, fontcolor=Colors.WHITE, fontsize=20, legend='Press Enter to restart')
    option1.draw()
    option2.draw()
    return display


# pause
def display_pause(screen):
    display = Text(screen, 25, 145, fontcolor=Colors.WHITE, legend='PAUSE')
    display.draw()
    return display


# mute
def display_mute(screen):
    display = Text(screen, 25, 85, fontcolor=Colors.WHITE, legend='MUTE')
    display.draw()
    return display


# functions that wait for user input, if q quit
def wait_for_key(key, keytype=KEYDOWN, frame_rate=30):
    p = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == keytype:
                if event.key == K_q: terminate(None)
                elif event.key == key: return None
        # limits fps to 50
        p.tick(frame_rate)


# edge case to check if the shape is line, for rotating
def is_line(tetromino):
    if tetromino == Shapes.LINE: return True
    else: return False


# modular function for actions
def down(grid):
    # break if tetromino froze
    if grid.tetromino is None:
        return
    grid.dropblocks()
    global block_clock
    block_clock = 0


def hard_drop(grid):
    # break if tetromino froze
    if grid.tetromino is None:
        return
    grid.harddrop()
    global block_clock
    block_clock = 0


def right(grid):
    # break if tetromino froze
    if grid.tetromino is None:
        return
    if not (grid.tetromino_at_the_border(K_RIGHT)):
        grid.erase_tetromino()
        grid.move_tetromino(K_RIGHT)
        grid.draw_tetromino()


def left(grid):
    # break if tetromino froze
    if grid.tetromino is None:
        return
    if not (grid.tetromino_at_the_border(K_LEFT)):
        grid.erase_tetromino()
        grid.move_tetromino(K_LEFT)
        grid.draw_tetromino()


def up(grid):
    # break if tetromino froze
    if grid.tetromino is None:
        return
    # move two instead of one if object is a line
    if check:
        if grid.tetromino_at_the_border(K_LEFT):
            for i in range(2): right(grid)
        elif grid.tetromino_at_the_border(K_RIGHT):
            for i in range(2): left(grid)
    elif grid.tetromino_at_the_border(K_LEFT): right(grid)
    elif grid.tetromino_at_the_border(K_RIGHT): left(grid)

    # check if tetromino is at the very bottom
    grid.erase_tetromino()
    try:
        grid.rotate_tetromino()
        main_grid.draw_tetromino()
    except AssertionError:
        grid.erase_tetromino()
        grid.move_tetromino(K_UP)
        grid.rotate_tetromino()
        grid.draw_tetromino()


def pause(grid):
    pause = display_pause(surface)
    wait_for_key(K_p)
    pause.erase()
    del pause


actions = {
    "113": terminate,
    "274": down,
    "115": down,
    "276": left,
    "97": left,
    "275": right,
    "100": right,
    "273": up,
    "119": up,
    "32": hard_drop,
    "304": hard_drop,
    "112": pause
}


# function that execute everything
pygame.init()
pygame.key.set_repeat(100, 1)
surface = pygame.display.set_mode((window_width, window_height))
block_size = 18
pygame.display.set_caption('Tetris')
fps_clock = pygame.time.Clock()
# pygame.mixer.music.load('/Users/Donovan/Desktop/References/script/Tetromino/music/level1.mp3')
pygame.mixer.music.load('./music/level1.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0)

# difficulty and ticks
frame_counter = 30
fps = 0
block_ticks = 10
block_clock = 0
checkpoint = 25
counter = 0
score = 0

# Generate containers
main_grid = sets.Grid(surface, 250, 25, square_x=17, square_y=33, square_size=block_size, forecolor=Colors.WHITE)
next_grid = sets.Grid(surface, 10 + 17 * (block_size+2) + 272, 25, square_x=6, square_y=6, square_size=block_size+2, forecolor=Colors.WHITE)
score_grid = Score(surface, 25, 25, fontcolor=Colors.WHITE, bgcolor=Colors.BLACK)
dcty_grid = Score(surface, 25, 355, fontcolor=Colors.WHITE, bgcolor=Colors.BLACK)
bklt_grid = Score(surface, 25, 415, fontsize=30, fontcolor=Colors.WHITE, bgcolor=Colors.BLACK)
main_grid.draw()
next_grid.draw()
dcty_grid.modifyscore(10 - block_ticks, label="Difficulty: {0}")
bklt_grid.modifyscore(checkpoint - counter, label="Blocks Left: {0}")
dcty_grid.draw()
bklt_grid.draw()
score_grid.draw()

# starting the game
mute = display_mute(surface)
pygame.mixer.music.pause()

# check edge cases if it's a line
tmp = random_tetromino()
check = is_line(tmp)

# sets current tetromino in current grid
main_grid.tetromino = sets.Tetromino(0, 7, tmp)
main_grid.draw_tetromino()
main_grid.drawblocks()
next_tetromino = random_tetromino()

# sets next tetromino in next grid
next_grid.tetromino = sets.Tetromino(1, 1, next_tetromino)
next_grid.draw_tetromino()
next_grid.drawblocks()

# start generation
while True:
    if fps == frame_counter / 10:
        block_clock += 1
        fps = 0

    # when counter reaches a check, difficulty increase
    if counter == checkpoint:
        counter = 0
        if block_ticks > 1: block_ticks -= 1
    if block_clock == block_ticks:
        main_grid.dropblocks()
        block_clock = 0

    # actions
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            try:
                actions[str(event.key)](main_grid)
            except KeyError:
                if str(event.key) == "109":
                    if mute:
                        pygame.mixer.music.unpause()
                        mute.erase()
                        mute = None
                    else:
                        pygame.mixer.music.pause()
                        mute = display_mute(surface)

    if not main_grid.tetromino:
        # check if it's a line
        if is_line(next_tetromino): check = True
        else: check = False
        add_score = main_grid.check_lines()
        score += add_score
        main_grid.tetromino = sets.Tetromino(0, 7, next_tetromino)

        # check if game is over
        try:
            main_grid.draw_tetromino()
        except:
            picker = display_game_over(surface)
            wait_for_key(K_RETURN)

        # updating grids
        next_tetromino = random_tetromino()
        next_grid.erase_tetromino()
        # sets next tetromino in next grid
        next_grid.tetromino = sets.Tetromino(1, 1, next_tetromino)
        next_grid.draw_tetromino()
        next_grid.drawblocks()
        dcty_grid.modifyscore(11-block_ticks, label="Difficulty: {0}")
        bklt_grid.modifyscore(checkpoint-counter, label="Blocks Left: {0}")
        score_grid.modifyscore(score)
        score_grid.redraw()
        dcty_grid.redraw()
        bklt_grid.redraw()
        counter += 1

    main_grid.drawblocks()
    fps_clock.tick(frame_counter)
    fps += 1




