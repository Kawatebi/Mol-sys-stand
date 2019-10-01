#!/usr/bin/env python
from glob import glob
import re
import pygame
import random
import time
import sys
import math
import threading
from os import path
from random import randint, choice
import RPi.GPIO as GPIO
from hx711 import HX711

GPIO.setwarnings(False)

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BG_COLOR = pygame.Color(255, 255, 255)

screen = pygame.display.set_mode((2000, 1030))

PLAYER_LEFT = 'left'
PLAYER_RIGHT = 'right'
MIN_WEIGHT = 0
MAX_WEIGHT = 2000
HEALTHY_IMAGE_INDEX_RANGE = [96, 97, 98]

background = pygame.image.load('images/startbackground.tif').convert()
background_large = pygame.transform.scale(background, (1900, 1000))

starttitle1 = pygame.image.load("images/starttitle1.png")
starttitle1_small = pygame.transform.scale(starttitle1, (1100, 700))

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
        self.rect.x = random.randrange(2000 - self.rect.width)
        self.rect.y = random.randrange(-100, -20)
        self.speedy = random.randrange(5, 10)
        self.speedx = random.randrange(-6, 6)

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > 1030 + 10 or self.rect.left < -25 or self.rect.right > 2000 + 20:
            self.rect.x = random.randrange(2000 - self.rect.width)
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
        screen.blit(background_large, (0, 0))

        # Draw / render
        all_sprites.draw(screen)

        #position of title on screen
        screen.blit(starttitle1_small, [400, 100])#, starttitle1_rect)

        # *after* drawing everything, flip the display
        pygame.display.update()    
    

def extract_index_from_image(image_path):
    p = re.compile(r'(\d+)\.jpg$')
    m = p.search(image_path)
    assert m
    return int(m.groups()[0])


def get_min_image_index_max_from_images(image_directory):
    images = glob(f'{image_directory}/*.jpg')
    indices = [extract_index_from_image(image) for image in images]
    return min(indices), max(indices)


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, name):
        super(Player, self).__init__()
        assert name in [PLAYER_LEFT, PLAYER_RIGHT]
        image_directory = f'./images/Henning Animations/Henning {name}/'
        image_index_min, image_index_max = get_min_image_index_max_from_images(
            image_directory)
        self.image_index_min = image_index_min
        self.image_index_max = image_index_max
        self.slope = (self.image_index_min - self.image_index_max) / \
            (MAX_WEIGHT - MIN_WEIGHT)
        self.yint = self.image_index_min - self.slope*MAX_WEIGHT
        self.player_images = [pygame.image.load(
            f'{image_directory}/Henning {name}{index:03}.jpg') for index in range(image_index_min, image_index_max + 1)]
        self.starting_weight = 0
        self.image_index = 0
        self.name = name
        self.image = self.player_images[self.image_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def set_starting_weight(self, starting_weight):
        self.starting_weight = starting_weight

    def get_image_index_for_weight(self, weight):
        image_index = int((weight + self.starting_weight)*self.slope + self.yint)
        if image_index < self.image_index_min:
            return self.image_index_min
        elif image_index > self.image_index_max:
            return self.image_index_max
        else:
            return image_index

    def set_weight(self, weight):
        self.weight = weight
        self.image_index = self.get_image_index_for_weight(weight)
#        print('self.image_index', self.image_index)

    def is_healthy(self):
        return self.image_index in HEALTHY_IMAGE_INDEX_RANGE

    def update(self):
        self.image = self.player_images[self.image_index]


def get_random_starting_weight():
    # Select from both sides of the tails
    ranges = [(0, 200), (1800, 2000)]
    return randint(*choice(ranges))


class Scale(object):
    def __init__(self, pin1, pin2, reference_unit):
        scale = HX711(pin1, pin2)
        scale.set_reading_format("MSB", "MSB")
        # calibrate value
        scale.set_reference_unit(reference_unit)
        scale.reset()
        scale.tare()
        self.scale = scale
    
    def tare(self):
        self.scale.tare()
    
    def read(self):
        newWeight = self.scale.get_weight(15)
        self.scale.power_down()
        self.scale.power_up()
        return newWeight



# Initiliase these only once as it can take time to load all of the images
player_left = Player(5, -20, PLAYER_LEFT)
player_right = Player(945, -20, PLAYER_RIGHT)
assert player_left.image_index_min == player_right.image_index_min and player_left.image_index_max == player_right.image_index_max
player_sprites = pygame.sprite.Group(player_left, player_right)
scale_left = Scale(5, 6, -22.5)
scale_right = Scale(23, 24, -22.7)


def game_loop():
    starting_weight = get_random_starting_weight()
    starting_weight = 0
    scale_left.tare()
    scale_right.tare()   
    player_left.set_starting_weight(starting_weight)
    player_right.set_starting_weight(starting_weight)

    running = True

    while running:
        pygame.time.Clock().tick(60)

        # Process input (events)
        for event in pygame.event.get():
            # check for closing window
            if event.type == pygame.QUIT:
                running = False
                break

        # get weight from scale
        weight_left = scale_left.read()        
        player_left.set_weight(weight_left)
        print('weight_left', weight_left, 'index_left', player_left.image_index)

        # repeat for right scale
        weight_right = scale_right.read()
        player_right.set_weight(weight_right)
        print('weight_right', weight_right, 'index_right', player_right.image_index)
        
        player_sprites.update()
        screen.fill(BG_COLOR)
        player_sprites.draw(screen)
        pygame.display.update()

        # Determine if one of the players has won
        winners = []
        for player in [player_left, player_right]:
            if player.is_healthy():
                winners.append(player)
                running = False

        if len(winners) == 1:
            print(f'Player {winners[0].name} wins!')

        if len(winners) == 2:
            print('A tie!')
            
            
#GPIO.cleanup()

def main_loop():
    # initialize pygame and create window
    #   showStartScreen()
    pygame.init()
    pygame.display.set_caption('Molecular Systems')
    showStartScreen()
    game_loop()
    print('in the main loop')

    # while True:
    # showGameOverScreen()


def main():
    main_loop()


if __name__ == '__main__':
    main()
