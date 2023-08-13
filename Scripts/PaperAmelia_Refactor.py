#
# Author: Amelia Sinclaire
# Copyright 2023
#

import pygame
import os
from Outfit import Article, Outfit, scale_img
from enum import Enum

Action = Enum('Action', ['NONE', 'EXIT', 'PREVIOUS_LAYER', 'NEXT_LAYER', 'PREVIOUS_ARTICLE', 'NEXT_ARTICLE',
                         'TOGGLE_ARTICLE', 'REMOVE_LAYER_ARTICLES', 'REMOVE_ALL_ARTICLES', 'TOGGLE_LAYER_LOCK'])


def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)


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
            # TODO toggle article control overlay
            # change current layer preview
            if event.key == pygame.K_DOWN:
                return Action.PREVIOUS_LAYER
            if event.key == pygame.K_UP:
                return Action.NEXT_LAYER
            # change current article preview
            if event.key == pygame.K_LEFT:
                return Action.PREVIOUS_ARTICLE
            if event.key == pygame.K_RIGHT:
                return Action.NEXT_ARTICLE
            # toggle article on current outfit
            if event.key == pygame.K_RETURN:
                return Action.TOGGLE_ARTICLE
            # remove all articles from current outfit
            if event.key == pygame.K_x and pygame.key.get_mods() & pygame.KMOD_CTRL:
                print('remove all')
                return Action.REMOVE_ALL_ARTICLES
            # remove all articles in current layer from current outfit
            if event.key == pygame.K_x:
                return Action.REMOVE_LAYER_ARTICLES
            # lock/unlock current layer
            if event.key == pygame.K_l:
                return Action.TOGGLE_LAYER_LOCK
        # save a screenshot
        # save current outfit
        # load outfit
        # toggle help overlay
        # toggle stats overlay
        # generate a random outfit and make it the current outfit (respect locked layers)
        # generate an outfit from weather data and make it the current outfit
        # open optimization menu
        #   change current article attribute
        #   optimize current article attribute
    return Action.NONE


def toggle_article(outfit, layer_idx, article_idx):
    layer_articles = list(filter(lambda a: a.layer == layer_idx, Article.articles))
    outfit.toggle_article(layer_articles[article_idx[layer_idx]])


def remove_layer_articles(outfit, layer_idx):
    to_be_removed = []
    for article in outfit.articles:
        if article.layer == layer_idx:
            to_be_removed.append(article)
    for article in to_be_removed:
        outfit.remove_article(article)


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
    print(Article.num_layers)
    print(Article.num_articles_per_layer)

    # Current Outfit = default outfit
    current_outfit = Outfit()
    current_outfit.load(default_outfit_file_path)
    current_outfit.locked_layers[0] = True  # lock base layer by default

    # temporary putting these variables here
    current_layer_idx = 1  # start on first layer above base layer (layer 0)
    current_article_idx = [0] * Article.num_layers
    for article in current_outfit.articles:  # initialize current_article_idx from current_outfit
        layer_articles = list(filter(lambda a: a.layer == article.layer, Article.articles))
        current_article_idx[article.layer] = layer_articles.index(article)

    # Viewer Outfit = empty outfit
    viewer_outfit = Outfit()
    viewer_outfit.toggle_article(Article.articles[1])

    action = Action.NONE
    while action is not Action.EXIT:
        action = handle_user_input()
        if action == Action.PREVIOUS_LAYER:
            current_layer_idx = clamp(current_layer_idx - 1, 0, Article.num_layers - 1)
        elif action == Action.NEXT_LAYER:
            current_layer_idx = clamp(current_layer_idx + 1, 0, Article.num_layers - 1)
        elif action == Action.PREVIOUS_ARTICLE:
            current_article_idx[current_layer_idx] = clamp(current_article_idx[current_layer_idx] - 1, 0, Article.num_articles_per_layer[current_layer_idx]-1)
        elif action == Action.NEXT_ARTICLE:
            current_article_idx[current_layer_idx] = clamp(current_article_idx[current_layer_idx] + 1, 0, Article.num_articles_per_layer[current_layer_idx]-1)
        elif action == Action.TOGGLE_ARTICLE:
            toggle_article(current_outfit, current_layer_idx, current_article_idx)
        elif action == Action.REMOVE_LAYER_ARTICLES:
            remove_layer_articles(current_outfit, current_layer_idx)
        elif action == Action.REMOVE_ALL_ARTICLES:
            current_outfit.remove_all_articles()
        elif action == Action.TOGGLE_LAYER_LOCK:
            current_outfit.toggle_lock(current_layer_idx)
        if action is not Action.NONE:
            # print(f'layer: {current_layer_idx}')
            # print(f'layer: {current_article_idx}')
            pass

        # update viewer outfit
        viewer_outfit.remove_all_articles()
        toggle_article(viewer_outfit, current_layer_idx, current_article_idx)

        # draw background
        screen.blit(background_sprite, (0, 0))
        screen.blit(background_sprite, (637, 0))
        # draw outfit
        current_outfit.draw(screen)
        viewer_outfit.draw(screen, (637, 0))
        # TODO draw overlay

        pygame.display.update()
        clock.tick(60)  # framerate
    pygame.quit()
    exit()


if __name__ == '__main__':
    screen = init_pygame(1274, 825)  # 637, 825
    clock = pygame.time.Clock()

    main(screen)
