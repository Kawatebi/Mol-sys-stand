#!/usr/bin/env python
import pygame
import random
import time
import sys
from os import path

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BG_COLOR = pygame.Color(255, 255, 255)


#set up screen size and surface size
WINDOWWIDTH = 1200
WINDOWHEIGHT = 650
HALF_WINDOWWIDTH = int(WINDOWWIDTH / 2)
HALF_WINDOWHEIGHT = int(WINDOWHEIGHT / 2)
THIRD_WINDOWWIDTH = int(WINDOWWIDTH / 3)
THIRD_WINDOWHEIGHT = int(WINDOWHEIGHT / 3)

screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

# 31 weight ranges related to the 31 frames/indices in the Player animation
weight_ranges = [1930,  # 0: Skinny
                 1859,
                 1788,
                 1717,
                 1646,
                 1575,
                 1504,
                 1433,
                 1362,
                 1328,
                 1294,
                 1260,
                 1234,
                 1208,
                 1182,
                 1166,
                 1140,
                 1114,
                 1088,
                 1054,
                 1020,
                 986,
                 915,
                 844,
                 773,
                 702,
                 631,
                 560,
                 489,
                 418,
                 200]  # 31: Overweight

MIN_WEIGHT = 0
MAX_WEIGHT = 2000
MIN_IMAGE_INDEX = 0
MAX_IMAGE_INDEX = len(weight_ranges)
HEALTHY_IMAGE_INDEX = 15


def get_image_index(weight):
    """
    Using the weight values to return an image index which refers to the Player image/index
    """
    if weight > MAX_WEIGHT:
        print('weight too big')
    if weight < MIN_WEIGHT:
        print('weight too small')
    for image_index, range_start in enumerate(weight_ranges):
        if weight >= range_start:
            return image_index
    else:
        print('no image index found')


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, image_index, name):
        super(Player, self).__init__()
        self.playerimages = [pygame.image.load(
            f'images/Henning_{index:02}.png') for index in range(len(weight_ranges))]

        # index value to get the image from the array initially it is 0
        self.image_index = image_index
        self.target_image_index = 0
        # now the image that we will display will be the index from the image array
        self.name = f'Player {name}'
        self.image = self.playerimages[self.image_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def set_target_image_index(self, target_image_index):
        self.target_image_index = target_image_index

    def set_image_index_and_image(self, image_index):
        self.image = self.playerimages[image_index]
        self.image_index = image_index

    def update(self):
        target_image_index = self.target_image_index
        image_index = self.image_index
        if image_index < target_image_index and image_index < MAX_IMAGE_INDEX:
            self.set_image_index_and_image(image_index + 1)
        elif image_index > target_image_index and image_index > MIN_IMAGE_INDEX:
            self.set_image_index_and_image(image_index - 1)


def main_loop():
    # preparing music settings
    pygame.mixer.pre_init(44100,16,2,4096)
    
    # initialize pygame and create window
    pygame.init()
    pygame.display.set_caption('Molecular Systems')

    #countdowns
    pygame.time.set_timer(pygame.USEREVENT, 1000)

    showStartScreen()
    instructions_screen()
    start_countdown()
    game_loop()
    print('in the main loop')
    timeup()
    player1win()
    player2win()
  #  timeup()


#text box

#if you want to change font - change path below
BASICFONT = ('c:/windows/fonts/archristy.ttf')

def draw_text(surf, text, size, x, y, colour):
    font = pygame.font.Font(BASICFONT, size)
    text_surface = font.render(text, True, colour)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    screen.blit(text_surface, text_rect)

#startscreen images and sprites
# Load background graphics
background = pygame.image.load('images/startbackground.tif').convert()
background_rect = background.get_rect()

starttitle1 = pygame.image.load("images/starttitle1.png")
starttitle1_small = pygame.transform.scale(starttitle1, (700, 450))

#blood cells and thyroid molecules
CELL_IMAGES =[pygame.image.load('images/cell0small.png').convert(),
              pygame.image.load('images/cell1small.png').convert(),
              pygame.image.load('images/cell12small.png').convert(),
              pygame.image.load('images/cell13small.png').convert(),
              pygame.image.load('images/thyroidsmall.png').convert(),
              pygame.image.load('images/thyroid2small.png').convert()]


# randomise cell images in intro
class Cells(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = random.choice(CELL_IMAGES)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WINDOWWIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -20)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > WINDOWHEIGHT + 10 or self.rect.left < -25 or self.rect.right > WINDOWWIDTH + 20:
            self.rect.x = random.randrange(WINDOWWIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(4, 10)


#add all sprites into single group

all_sprites = pygame.sprite.Group()
cells = pygame.sprite.Group()

for i in range(8):
    m = Cells()
    all_sprites.add(m)
    cells.add(m)


def showStartScreen():

    running = True
    while running:

    # keep loop running at the right speed
        pygame.time.Clock().tick(60)
    # Process input (events)
        for event in pygame.event.get():
        # check for closing window
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False
            if event.type == pygame.KEYUP:
                running = False

        all_sprites.update()
#Background
        screen.blit(background, background_rect)

        # Draw / render
        all_sprites.draw(screen)

        #position of title on screen
        screen.blit(starttitle1_small, [250, 100])#, starttitle1_rect)

        # *after* drawing everything, flip the display
        pygame.display.update()


def instructions_screen():

    waiting = True
    while waiting:
        pygame.time.Clock().tick(5)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False
                continue

        screen.blit(background, background_rect)
        draw_text(screen, "Insert instructions here....!", 64, WINDOWWIDTH / 2, WINDOWHEIGHT / 4, BLUE)
        pygame.display.update()


def start_countdown():
    counter, text = 3, '3'.rjust(3)
 #   pygame.time.set_timer(pygame.USEREVENT, 1000)
    font = pygame.font.SysFont('Arial', 300)

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT:
                counter -= 1
                text = str(counter).rjust(3) if counter > 0 else 'GO!'
            if counter == 0:
                waiting = False
            if event.type == pygame.QUIT: break
        else:
            screen.fill((255, 255, 255))
            screen.blit(font.render(text, True, (0, 0, 0)), (385, 130))
            pygame.display.flip()
            pygame.time.Clock().tick(60)
            continue



def game_loop():
    player1 = Player(5, 5, 30, '1')
    player2 = Player(645, 5, 0, '2')
    player_sprites = pygame.sprite.Group(player1, player2)

    player1.set_target_image_index(0)
    player2.set_target_image_index(30)

    countdown, text = 5, '5'.rjust(3)
    pygame.time.set_timer(pygame.USEREVENT, 1000)
    font = pygame.font.SysFont('Arial', 300)

    running = True

    while running:
        pygame.time.Clock().tick(5)
     # Process input (events)
        for event in pygame.event.get():
            # check for closing window
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYUP:
                running = False
                break
        player_sprites.update()
        screen.fill(WHITE)
        player_sprites.draw(screen)
        pygame.display.update()
        for player in [player1, player2]:
            if player.image_index == HEALTHY_IMAGE_INDEX:
                print(f'{player.name} wins!')
                return


def flashbackground(color=WHITE, animationSpeed=10):
    origSurf = screen.copy()
    flashSurf = pygame.Surface(screen.get_size())
    flashSurf = flashSurf.convert_alpha()
    r, g, b = color
    while True:
        pygame.time.Clock().tick(30)
        for i in range(3): # do the flash 3 times
            for start, end, step in ((0, 255, 1), (255, 0, -1)):
                # The first iteration in this loop sets the following for loop
                # to go from 0 to 255, the second from 255 to 0.
                for alpha in range(start, end, animationSpeed * step): # animation loop
                    # alpha means transparency. 255 is opaque, 0 is invisible
                    flashSurf.fill((r, g, b, alpha))
                    screen.blit(origSurf, (0, 0))
                    screen.blit(flashSurf, (0, 0))
                    pygame.display.update()
        break

def timeup():
    flashbackground()
    screen.fill(BLACK)
    draw_text(screen, "TIME'S UP!'", 130, WINDOWWIDTH / 2, WINDOWHEIGHT / 8, WHITE)
    draw_text(screen, "Game Over", 80, WINDOWWIDTH / 2, WINDOWHEIGHT / 2, WHITE)

    waiting = True
    while waiting:
        pygame.time.Clock().tick(1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False
                continue

        pygame.display.update()

def player1win():
    flashbackground()
    screen.fill(WHITE)
    draw_text(screen, "You Won!", 80, 300, 300, GREEN)
    draw_text(screen, "They Won", 80, 900, 300, BLUE)

    # Play background music
    pygame.mixer.music.load('music/GSTone.mp3')
    pygame.mixer.music.set_volume(1)
    pygame.mixer.music.play(-1)
    
    waiting = True
    while waiting:
        pygame.time.Clock().tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False
                return
        pygame.display.update()
    


def player2win():
    flashbackground()
    screen.fill(WHITE)
    draw_text(screen, "They Won", 80, 300, 300, BLUE)
    draw_text(screen, "You Won!", 80, 900, 300, GREEN)
    
    # Play background music
    pygame.mixer.music.load('music/GSTone.mp3')
    pygame.mixer.music.set_volume(1)
    pygame.mixer.music.play(-1)

    waiting = True
    while waiting:
        pygame.time.Clock().tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False
                return

        pygame.display.update()

def main():
    main_loop()



if __name__ == '__main__':
    main()