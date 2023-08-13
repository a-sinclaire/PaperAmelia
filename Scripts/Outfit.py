#
# Author: Amelia Sinclaire
# Copyright 2023
#

import pygame
import os


def scale_img(img, scale):
    return pygame.transform.scale(img, (img.get_width() / scale, img.get_height() / scale))


class Article:
    csv_titles = ''
    articles = []
    asset_path = ''
    scale = 4.0
    highest_priority = -1
    num_layers = 0
    num_articles_per_layer = []

    def __init__(self, layer, file_path, csv_data, priority=0):
        self.layer = layer
        self.file_path = file_path
        self.csv_data = csv_data
        self.priority = priority
        self.sprite = None
        Article.articles.append(self)

    def load_sprite(self):
        self.sprite = pygame.image.load(self.file_path)
        self.sprite = scale_img(self.sprite, Article.scale)
        print(f'LOADED: {self.file_path}')

    def draw(self, screen, pos=(0, 0)):
        if self.sprite is None:
            self.load_sprite()
        screen.blit(self.sprite, pos)

    @staticmethod
    def search(csv_data):
        for article in Article.articles:
            if article.csv_data == csv_data:
                return article
        return None

    @staticmethod
    def load_articles(asset_path, csv_file_path):
        Article.asset_path = asset_path
        with open(csv_file_path, 'r') as f:
            lines = f.readlines()

        Article.csv_titles = lines[0]
        for csv_line in lines[1:]:  # skip csv header
            Article.load_article(csv_line)
        Article.update()

    @staticmethod
    def load_article(csv_line):
        if csv_line.strip() == '':  # ignore blank lines
            return None

        properties = csv_line.split(',')
        layer = int(properties[0])
        article_file_path = os.path.join(Article.asset_path, properties[1])

        Article.highest_priority += 1
        article = Article(layer, article_file_path, csv_line, priority=Article.highest_priority)
        Article.sort()
        return article

    @staticmethod
    def sort():
        Article.articles.sort(key=lambda a: (a.layer, a.priority))

    @staticmethod
    def update():
        Article.num_layers = 1
        Article.num_articles_per_layer = []

        article_counter = 0
        Article.sort()
        last_layer = Article.articles[0].layer
        for article in Article.articles:
            if article.layer != last_layer:
                Article.num_articles_per_layer.append(article_counter)
                article_counter = 0
                Article.num_layers += 1
            article_counter += 1
            last_layer = article.layer
        Article.num_articles_per_layer.append(article_counter)


class Outfit:
    def __init__(self, articles=[]):
        self.articles = articles
        self.sorted = False
        self.locked_layers = [False] * Article.num_layers

    def toggle_article(self, article):
        if article is None:
            return
        if self.locked_layers[article.layer]:  # do nothing if layer is locked
            return

        self.sorted = False
        if article in self.articles:
            self.articles.remove(article)
            return
        self.articles.append(article)

    def toggle_lock(self, layer_idx):
        self.locked_layers[layer_idx] = not self.locked_layers[layer_idx]

    def remove_article(self, article):
        if article is None:
            return
        if self.locked_layers[article.layer]:  # do nothing if layer is locked
            return

        self.sorted = False
        if article in self.articles:
            self.articles.remove(article)

    def remove_all_articles(self):
        to_be_removed = []
        for article in self.articles:
            to_be_removed.append(article)
        for article in to_be_removed:
            self.remove_article(article)

    def sort(self):
        self.articles.sort(key=lambda a: (a.layer, a.priority))
        self.sorted = True

    def draw(self, screen, pos=(0, 0)):
        if not self.sorted:
            self.sort()

        for a in self.articles:
            a.draw(screen, pos)

    def save(self, file_path):
        lines = [Article.csv_titles]
        for a in self.articles:
            lines.append(a.csv_data)
        with open(file_path, 'w+') as f:
            f.writelines(lines)

    def load(self, file_path):
        self.articles = []
        with open(file_path, 'r') as f:
            lines = f.readlines()
        for csv_line in lines[1:]:  # first line has header data for *some reason*
            if csv_line.strip() == '':  # ignore blank lines
                continue
            article = Article.search(csv_line)  # check if article is already in Article list
            if article is None:
                article = Article.load_article(csv_line)
            self.toggle_article(article)

        Article.update()
