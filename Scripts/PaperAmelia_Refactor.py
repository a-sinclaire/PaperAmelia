#
# Author: Amelia Sinclaire
# Copyright 2023
#

import pygame
import os
import copy
from Outfit import Article, Outfit, scale_img
from Button import Button, ArticleButton
from Undo import UndoBuffer
from enum import Enum

Action = Enum('Action', ['NONE', 'EXIT', 'PREVIOUS_LAYER', 'NEXT_LAYER', 'PREVIOUS_ARTICLE', 'NEXT_ARTICLE',
                         'TOGGLE_ARTICLE', 'REMOVE_LAYER_ARTICLES', 'REMOVE_ALL_ARTICLES', 'TOGGLE_LAYER_LOCK',
                         'UNDO', 'REDO', 'SAVE', 'LOAD', 'RANDOM'])


class PaperAmeliaContext:
    def __init__(self, default_outfit_file_path=None, max_undos=10):
        self.undo_buffer = UndoBuffer(max_undos=max_undos)

        self.current_outfit = Outfit()
        if default_outfit_file_path is not None:
            self.current_outfit.load(default_outfit_file_path)
        self.save_state()
        self.viewer_outfit = Outfit()
        self.viewer_outfit.toggle_article(Article.articles[1])

        self.current_layer_id = 1
        self.current_article_ids = [0] * Article.num_layers

        self.set_current_article_ids()

    def set_current_article_ids(self):
        for article in self.current_outfit.articles:  # initialize current_article_idx from current_outfit
            layer_articles = list(filter(lambda a: a.layer == article.layer, Article.articles))
            self.current_article_ids[article.layer] = layer_articles.index(article)

    def previous_layer(self):
        self.current_layer_id = clamp(self.current_layer_id - 1, 0, Article.num_layers - 1)

    def next_layer(self):
        self.current_layer_id = clamp(self.current_layer_id + 1, 0, Article.num_layers - 1)

    def previous_article(self):
        self.current_article_ids[self.current_layer_id] = clamp(self.current_article_ids[self.current_layer_id] - 1, 0,
                                                                Article.num_articles_per_layer[
                                                                    self.current_layer_id] - 1)

    def next_article(self):
        self.current_article_ids[self.current_layer_id] = clamp(self.current_article_ids[self.current_layer_id] + 1, 0,
                                                                Article.num_articles_per_layer[
                                                                    self.current_layer_id] - 1)

    def toggle_article(self, outfit=None):
        if outfit is None:
            outfit = self.current_outfit
        layer_articles = list(filter(lambda a: a.layer == self.current_layer_id, Article.articles))
        outfit.toggle_article(layer_articles[self.current_article_ids[self.current_layer_id]])
        if outfit == self.current_outfit:
            print('save state after toggle')
            self.save_state()

    def save_state(self):
        self.undo_buffer.add(self.current_outfit)

    def remove_layer_articles(self, outfit=None):
        if outfit is None:
            outfit = self.current_outfit
        outfit.remove_layer_articles(self.current_layer_id)
        if outfit == self.current_outfit:
            print('save state after remove layer')
            self.save_state()

    def remove_all_articles(self, outfit=None):
        if outfit is None:
            outfit = self.current_outfit
        outfit.remove_all_articles()
        if outfit == self.current_outfit:
            print('save state after remove all')
            self.save_state()

    def toggle_layer_lock(self):
        self.current_outfit.toggle_lock(self.current_layer_id)

    def undo(self):
        self.current_outfit = self.undo_buffer.undo()

    def redo(self):
        self.current_outfit = self.undo_buffer.redo()

    def randomize_outfit(self, outfit=None):
        if outfit is None:
            outfit = self.current_outfit
        outfit.randomize()
        if outfit == self.current_outfit:
            self.set_current_article_ids()
            print('save state after randomize')
            self.save_state()

    def save(self):
        self.current_outfit.save()

    def load(self):
        self.current_outfit.load()
        self.set_current_article_ids()

    def draw(self, screen, pos=(0, 0), outfit=None):
        if outfit is None:
            outfit = self.current_outfit
        outfit.draw(screen, pos)


def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)


def init_pygame(width, height):
    # my_font = pygame.font.SysFont(name='comicsans', size=24)
    pygame.init()
    pygame.display.set_caption("Paper Amelia")  # window title
    pygame.font.init()
    return pygame.display.set_mode((width, height))  # return screen


def handle_user_input(paper_amelia, buttons):
    events = pygame.event.get()
    # check for mouse hover
    for button in buttons:
        button.update(events)

    for event in events:
        if event.type == pygame.QUIT:
            return Action.EXIT
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return Action.EXIT
            # TODO: toggle article control overlay
            # change current layer preview
            if event.key == pygame.K_DOWN:
                paper_amelia.previous_layer()
            if event.key == pygame.K_UP:
                paper_amelia.next_layer()
            # change current article preview
            if event.key == pygame.K_LEFT:
                paper_amelia.previous_article()
            if event.key == pygame.K_RIGHT:
                paper_amelia.next_article()
            # toggle article on current outfit
            if event.key == pygame.K_RETURN:
                paper_amelia.toggle_article()
            # remove all articles from current outfit (respect locked layers)
            if event.key == pygame.K_x and pygame.key.get_mods() & pygame.KMOD_CTRL:
                paper_amelia.remove_all_articles()
            # remove all articles in current layer from current outfit (respect locked layers)
            if event.key == pygame.K_x:
                paper_amelia.remove_layer_articles()
            # save current outfit
            if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                paper_amelia.save()
            # load outfit
            if event.key == pygame.K_l and pygame.key.get_mods() & pygame.KMOD_CTRL:
                paper_amelia.load()
            # lock/unlock current layer
            if event.key == pygame.K_l:
                paper_amelia.toggle_layer_lock()
            # undo/redo action
            if event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                paper_amelia.undo()
                update_article_buttons_outfits(buttons, paper_amelia.current_outfit)
            if event.key == pygame.K_y and pygame.key.get_mods() & pygame.KMOD_CTRL:
                paper_amelia.redo()
                update_article_buttons_outfits(buttons, paper_amelia.current_outfit)
            # save a screenshot
            # toggle help overlay
            # toggle stats overlay
            # generate a random outfit and make it the current outfit (respect locked layers)
            if event.key == pygame.K_r:
                paper_amelia.randomize_outfit()
            # generate an outfit from weather data and make it the current outfit
            # open optimization menu
            #   change current article attribute
            #   optimize current article attribute
    return Action.NONE


def article_button_callback(outfit, article):
    outfit.toggle_article(article)


def create_article_buttons(outfit):
    buttons = pygame.sprite.Group()
    button_region_x = 1074
    button_region_y = 0
    button_region_w = 200
    button_region_h = 800
    button_w = 100
    button_h = 100
    x_location = button_region_x
    y_location = button_region_y
    active = True
    for article in Article.articles:
        if x_location >= button_region_x + button_region_w:
            x_location = button_region_x
            y_location += button_h
        if y_location >= button_region_y + button_region_h:
            y_location = button_region_y
            active = False
        buttons.add(ArticleButton(pygame.Rect(x_location, y_location, button_w, button_h), article_button_callback,
                                  outfit, article, active=active, text=''))
        x_location += button_w

    return buttons


def update_article_buttons_outfits(buttons, current_outfit):
    for button in buttons:
        button.outfit = current_outfit


def main(screen):
    directory = os.path.dirname(__file__)
    asset_path = os.path.join(directory, '../Assets/')
    csv_file_path = os.path.join(asset_path, 'articles.csv')
    background_file_path = os.path.join(asset_path, 'BACKGROUND.png')
    default_outfit_file_path = os.path.join(asset_path, 'default_outfit.outfit')
    # default_outfit_file_path = 'C:/Users/lader/Desktop/my_outfit.csv'

    # set scale
    Article.scale = 4.0

    # load background sprite
    background_sprite = pygame.image.load(background_file_path)
    background_sprite = scale_img(background_sprite, Article.scale)
    print(f'LOADED: {background_file_path}')

    # load in all the available articles from the database
    Article.load_articles(asset_path, csv_file_path)

    # Setup Main Context object
    paper_amelia = PaperAmeliaContext(default_outfit_file_path, max_undos=10)

    # Create Button
    test_button = Button(pygame.Rect(0, 0, 60, 60), lambda: print('AHHH!'), active=True, text='',
                         icon_path=os.path.join(asset_path, 'test_icon.png'))
    ArticleButton.article_thumbs_file_path = os.path.join(asset_path, 'Article_Thumbnails/')
    print(f'path: {ArticleButton.article_thumbs_file_path}')
    buttons = create_article_buttons(paper_amelia.current_outfit)

    action = Action.NONE
    while action is not Action.EXIT:
        action = handle_user_input(paper_amelia, buttons)

        # update viewer outfit
        paper_amelia.remove_all_articles(outfit=paper_amelia.viewer_outfit)
        paper_amelia.toggle_article(outfit=paper_amelia.viewer_outfit)

        # draw background
        screen.blit(background_sprite, (0, 0))
        screen.blit(background_sprite, (637, 0))
        # draw outfit(s)
        paper_amelia.draw(screen)
        paper_amelia.draw(screen, (637, 0), paper_amelia.viewer_outfit)
        # TODO: draw overlay
        # draw buttons
        for button in buttons:
            button.draw(screen)

        pygame.display.update()
        clock.tick(60)  # framerate
    pygame.quit()
    exit()


if __name__ == '__main__':
    screen = init_pygame(1274, 825)  # 637, 825
    clock = pygame.time.Clock()

    main(screen)
