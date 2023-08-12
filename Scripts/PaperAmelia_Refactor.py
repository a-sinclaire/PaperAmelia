import pygame
from Outfit import Article
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

    article = Article(1, 'C:\\Users\\lader\\Desktop\\PaperAmelia\\Assets\\4_BEE_SHIRT.png', 1)
    articleb = Article(1, 'C:\\Users\\lader\\Desktop\\PaperAmelia\\Assets\\3_TOMMYS.png', 1)

    while action is not Action.EXIT:
        action = handle_user_input()

        article.draw(screen)
        articleb.draw(screen)
        pygame.display.update()
        clock.tick(60)  # framerate


if __name__ == '__main__':
    screen = init_pygame(600, 800)
    clock = pygame.time.Clock()

    main(screen)
