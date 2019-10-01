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
from natsort import natsorted

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


def get_images_from_directory(image_directory):
    images = natsorted(glob(f'{image_directory}/*.jpg'))
    return images

class Dancer(pygame.sprite.Sprite):
    def __init__(self, x, y, name):
        super(Dancer, self).__init__()
        assert name in [PLAYER_LEFT, PLAYER_RIGHT]
        image_directory = f'./images/Henning Animations/Dancing/{name}/'
        images = get_images_from_directory(image_directory)
        self.images = [pygame.image.load(images[i]) for i in range(0, len(images), 5)]
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
    def set_should_dance(self, should_dance):
        self.should_dance = should_dance
        
    def update(self):
        if self.should_dance:
            self.index = self.index + 1 % len(self.images)
            self.image = self.images[self.index]
    

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, name):
        super(Player, self).__init__()
        assert name in [PLAYER_LEFT, PLAYER_RIGHT]
        image_directory = f'./images/Henning Animations/Henning {name}/'
        images = get_images_from_directory(image_directory)
        self.player_images = [pygame.image.load(images[i]) for i in range(0, len(images), 3)]
        self.image_index_min = 0
        self.image_index_max = len(self.player_images) - 1
        healthy_index = int(self.image_index_max / 2)
        self.healthy_image_index_range = range(healthy_index-1, healthy_index+2)
        self.slope = (self.image_index_min - self.image_index_max) / (MAX_WEIGHT - MIN_WEIGHT)
        self.yint = self.image_index_min - self.slope*MAX_WEIGHT
        self.starting_weight = 0
        self.image_index = 0
        self.name = name
        self.image = self.player_images[self.image_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.healthy = False

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
        self.healthy = self.image_index in self.healthy_image_index_range
#        print('self.image_index', self.image_index)

    def is_healthy(self):
        return self.healthy

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
scale_right = Scale(23, 24, -25.7)

dancer_left = Dancer(5, -20, PLAYER_LEFT)
dancer_right = Dancer(945, -20, PLAYER_RIGHT)
dancer_sprites = pygame.sprite.Group(dancer_left, dancer_right)

def dance_loop(winners):
    print(winners)
    print(PLAYER_LEFT in winners)
    print(PLAYER_RIGHT in winners)
    dancer_left.set_should_dance(PLAYER_LEFT in winners)
    dancer_right.set_should_dance(PLAYER_RIGHT in winners)
    
    running = True

    while running:
        pygame.time.Clock().tick(15)

        # Process input (events)
        for event in pygame.event.get():
            # check for closing window
            if event.type == pygame.QUIT:
                running = False
                break

        dancer_sprites.update()
        screen.fill(BG_COLOR)
        dancer_sprites.draw(screen)
        pygame.display.update()
        print('running', running)


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
                winners.append(player.name)
            
        if winners:
            print(winners)
            return winners
            
        
            
            
#GPIO.cleanup()

def main_loop():
    # initialize pygame and create window
    #   showStartScreen()
    pygame.init()
    pygame.display.set_caption('Molecular Systems')
    winners = game_loop()
    dance_loop(winners)
    print('in the main loop')

    # while True:
    # showGameOverScreen()


def main():
    main_loop()


if __name__ == '__main__':
    main()