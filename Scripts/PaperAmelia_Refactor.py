#
# Author: Amelia Sinclaire
# Copyright 2023
#

import pygame
import os
from Outfit import Article, Outfit, scale_img
from enum import Enum

Action = Enum('Action', ['NONE', 'EXIT'])


def init_pygame(width, height):
    # my_font = pygame.font.SysFont(name='comicsans', size=24)
    pygame.init()
    pygame.display.set_caption("Paper Amelia")  # window title
    pygame.font.init()
    return pygame.display.set_mode((width, height))  # return screen


def handle_user_input():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return Action.EXIT
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return Action.EXIT
    return Action.NONE


def main(screen):
    directory = os.path.dirname(__file__)
    asset_path = os.path.join(directory, '../Assets/')
    csv_file_path = os.path.join(asset_path, 'articles.csv')
    background_file_path = os.path.join(asset_path, 'BACKGROUND.png')
    default_outfit_file_path = os.path.join(asset_path, 'default_outfit.csv')

    # set scale
    Article.scale = 4.0

    # load background sprite
    background_sprite = pygame.image.load(background_file_path)
    background_sprite = scale_img(background_sprite, Article.scale)
    print(f'LOADED: {background_file_path}')

    # load in all the available articles from the database
    Article.load_articles(asset_path, csv_file_path)

    # Current Outfit = default outfit
    current_outfit = Outfit()
    current_outfit.load(default_outfit_file_path)

    action = Action.NONE
    while action is not Action.EXIT:
        action = handle_user_input()

        # draw background
        screen.blit(background_sprite, (0, 0))

        # draw outfit
        current_outfit.draw(screen)

        # TODO draw overlay

        pygame.display.update()
        clock.tick(60)  # framerate
    pygame.quit()
    exit()


if __name__ == '__main__':
    screen = init_pygame(637, 825)
    clock = pygame.time.Clock()

    main(screen)
