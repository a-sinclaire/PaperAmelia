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


def load_articles(directory, csv_file_name):
    csv_file_path = os.path.join(directory, csv_file_name)
    with open(csv_file_path, 'r') as f:
        lines = f.readlines()
    for line in lines[1:]:
        if line.strip() == '':
            continue
        properties = line.split(',')
        layer = properties[0]
        article_file_path = os.path.join(directory, properties[1])
        Article(layer, article_file_path)


def main(screen):
    action = Action.NULL
    directory = os.path.dirname(__file__)
    directory = os.path.join(directory, '../Assets/')

    load_articles(directory, 'directory_no_nan.csv')
    outfit = Outfit(Article.articles[4:7])
    outfit.toggle_article(Article.articles[5])

    while action is not Action.EXIT:
        action = handle_user_input()

        outfit.draw(screen)
        pygame.display.update()
        clock.tick(60)  # framerate


if __name__ == '__main__':
    screen = init_pygame(600, 800)
    clock = pygame.time.Clock()

    main(screen)
