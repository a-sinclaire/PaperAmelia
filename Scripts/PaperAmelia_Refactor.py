import pygame
import os
from Outfit import Article, Outfit
from enum import Enum

Action = Enum('Action', ['NULL', 'EXIT'])


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
    return Action.NULL


def main(screen):
    action = Action.NULL
    directory = os.path.dirname(__file__)
    directory = os.path.join(directory, '../Assets/')
    csv_file_name = 'articles.csv'
    csv_file_path = os.path.join(directory, csv_file_name)

    Article.load_articles(directory, csv_file_path)

    outfit = Outfit(Article.articles[7:9])
    outfit.load(os.path.join(directory, 'outfit.csv'))

    while action is not Action.EXIT:
        action = handle_user_input()

        outfit.draw(screen)
        pygame.display.update()
        clock.tick(60)  # framerate


if __name__ == '__main__':
    screen = init_pygame(600, 800)
    clock = pygame.time.Clock()

    main(screen)
